# Gentoo rsync backup main program
#
# Copyright (c) 2014 Johnny Wezel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import argparse
from contextlib import contextmanager
import logging
import sys
import itertools
import glob
import subprocess
import datetime
import logging.config
import pwd
import time

import paramiko
import yaml
import os
import blist
from . import _version

DEFAULT_CONFIG_FILE = os.path.expanduser('~/.local/etc/grbackup')
DEFAULT_PRUNE = [
    '/tmp',
    '/proc',
    '/sys',
    '/dev',
    '/mnt',
    '/var/tmp',
    '/var/run',
    '/var/cache',
    '/run',
    '/lost+found'
]
PKG_DB = '/var/db/pkg'
DEFAULT_LOG_FILE = '/var/log/grbackup'
DEFAULT_LOG_BACKUP_COUNT = 8
DEFAULT_LOG_SIZE = 4194304
DEFAULT_SSH_PORT = 22
DEFAULT_GENERATIONS = 30
VERSION_INFO = """grbackup %s
Copyright (c) 2014 Johnny Wezel
License: GNU GPL version 3 or later <http://gnu.org/licenses/gpl.html>
This is free software: you are free to change and redistribute it.
There is NO WARRANTY, to the extent permitted by law.""" % _version

class ConfigurationError(RuntimeError):
    """
    Configuration error
    """

class Ssh(object):
    """
    SSH connection
    """

    def __init__(self, host, port, user, passwd):
        """
        Create a Ssh object
        """
        self.connection = None
        self.host = host
        self.port = port
        self.user = user
        self.passwd = passwd

    def __enter__(self):
        self.connection = paramiko.SSHClient()
        self.connection.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        self.connection.load_host_keys(os.path.join(self.passwd.pw_dir, '.ssh', 'known_hosts'))
        self.connection.connect(self.host, self.port, self.user)
        t = self.connection.get_transport()
        t.set_keepalive(30)
        return self.connection

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.connection.close()
        self.connection = None

class Version(argparse.Action):
    """
    Action: Display version
    """

    def __call__(self, *args, **kw):
        """
        Display version
        """
        print VERSION_INFO
        sys.exit(0)

def Filesize(path):
    """
    Get file size

    :param path: path to file
    :type path: str
    :return: file size
    :rtype: int
    """
    try:
        return os.stat(path).st_size
    except:
        return 0

def Walk(root, prune=None, exclude=None):
    """
    Scan root

    :param root: start directory
    :type root: str
    :param prune: optional list of directories to prune
    :type prune: blist.sortedlist
    :param exclude: optional list of files to exclude
    :type exclude: blist.sortedlist
    :return: generator returning tuples of (path, file-size)
    :rtype: generator
    """
    if prune is None:
        prune = []
    if exclude is None:
        exclude = []
    for dir, dirs, files in os.walk(root):
        for d in dirs[:]:
            dd = os.path.join(dir, d)
            if dd in prune or os.path.exists(os.path.join(dd, '.no-backup')):
                dirs.remove(d)
            else:
                yield dd, Filesize(dd)
        for f in files:
            ff = os.path.join(dir, f)
            if ff not in exclude:
                yield ff, Filesize(ff)

def Backup(config):
    """
    Backup

    :param config: Configuration
    :type config: dict
    """
    # Start
    log = logging.getLogger('grbackup.backup')
    # Get configuration
    if 'destination' in config:
        dest = config['destination']
        try:
            directory = dest['directory']
        except KeyError:
            raise ConfigurationError('Configuration needs a "directory" entry in the "destination" section')
        directory = directory.format(**os.environ)
        passwd = pwd.getpwuid(os.geteuid())
        user = dest.get('user', passwd.pw_name)
        host = dest.get('host')
        port = dest.get('port', DEFAULT_SSH_PORT)
        maxgen = dest.get('generations', DEFAULT_GENERATIONS)
        if maxgen < 1:
            log.warn('Maximum number of generations < 1 (assuming 1)')
            maxgen = 1
    else:
        raise ConfigurationError('Configuration needs a "destination" section')
    ssh = Ssh(host, port, user, passwd)
    timedir = datetime.datetime.now().strftime('%F-%T')
    if host:
        destination = '{host}:{directory}/{timedir}'.format(**locals())
    else:
        destination = '{directory}/{timedir}'.format(**locals())
    prune = blist.sortedlist(config['prune'])
    log.info('directory=%s, user=%s, host=%s, port=%d', directory, user, host, port)
    # Find last backup
    with ssh as connection:
        cmdin, cmdout, cmderr = connection.exec_command('ls -d %s/????-??-??-??:??:??' % directory)
        error = cmderr.read()
        if error and error.endswith('No such file or directory\n'):
            cmdin, cmdout, cmderr = connection.exec_command('mkdir -p %s' % directory)
            error = cmderr.read()
            if error:
                log.critical(error)
                log.info('Aborting')
                return
            else:
                log.info('Backup directory %s created' % directory)
                backups = []
            lastBackup = None
        else:
            backups = [line.rstrip() for line in cmdout.readlines()]
            log.debug('All backups: %s', backups)
            lastBackup = backups[-1] if len(backups) > 0 else None
            log.info('Last backup: %s', lastBackup)
    # Generate the list of files belonging to Gentoo packages
    gentooFiles = blist.sortedlist(
        e[1] for e in (
            f.rstrip('\r\n').split()
            for f in itertools.chain(*(open(i).readlines() for i in glob.glob(PKG_DB + '/*/*/CONTENTS')))
        )
        if e[0] != 'dir'
    )
    log.info('Gentoo exempted files: %d', len(gentooFiles))
    # Generate the list of files to backup
    findFiles, fileSizes = itertools.tee(itertools.chain.from_iterable(Walk(r, prune) for r in config['roots']))
    totalSize = float(sum(e[1] for e in fileSizes))
    unit = 0
    while totalSize > 1024:
        totalSize /= 1024.
        unit += 1
    log.info('Backup amount from files: %3.3g%s', totalSize, ('', 'K', 'M', 'G', 'T', 'P', 'E')[unit])
    # Setup rsync command
    rsyncCmd = ['rsync']
    extra = []
    if lastBackup:
        extra.append('--link-dest=%s' % os.path.join(directory, lastBackup))
    rsyncCmd.extend([
        '--archive',
        '--verbose',
        '--compress',
        '--log-file=/tmp/rsync-backup-{}-{}.log'.format(host, user),
        '--stats',
        '--human-readable',
        '--partial',
        '--files-from=-',
        '--rsh=ssh -p %d -l %s' % (port, user)
    ] + extra + [
        '/',
        destination
    ])
    outFile = open('/tmp/rsync-backup-{}-{}.out'.format(host, user), 'w')
    errFile = open('/tmp/rsync-backup-{}-{}.err'.format(host, user), 'w')
    # Run rsync command
    rsyncRun = subprocess.Popen(rsyncCmd, stdin=subprocess.PIPE, stdout=outFile, stderr=errFile)
    rsyncRun.stdin.writelines(f[0] + '\n' for f in findFiles if f[0] not in gentooFiles)
    rsyncRun.stdin.close()
    log.info('Backup file list transmitted - waiting for rsync')
    t1 = time.time()
    rsyncRun.wait()
    t2 = time.time()
    timeRequired = int(t2 - t1 + 1)
    log.info('Rsync finished')
    # Remove backups that exceed maximum number of generations
    if len(backups) + 1 > maxgen:
        rmList = backups[:len(backups) + 1 - maxgen]
        log.info('Removing %d old backups (max. is %d)', len(rmList), maxgen)
        log.debug('Changing access for removal: %s', ', '.join(rmList))
        with ssh as connection:
            cmdin, cmdout, cmderr = connection.exec_command(
                'chmod -R u+rwx %s' % ' '.join(rmList), timeout=len(rmList) * 3600
            )
            error = cmderr.read()
            if error:
                log.error(error)
            log.debug('Removing backups %s', ', '.join(rmList))
            cmdin, cmdout, cmderr = connection.exec_command('rm -rf %s' % ' '.join(rmList), timeout=len(rmList) * 7200)
            error = cmderr.read()
        if error:
            log.error(error)

def Main():
    """
    Main program
    :return: 0 if no errors occurred
    :rtype: int
    """
    config = {
        'logging': {
            'version': 1,
            'formatters': {
                'default': {
                    'format': '%(asctime)s:%(name)-24s:%(levelname)s: %(message)s'
                }
            },
            'handlers': {
                'default': {
                    'class': 'logging.handlers.RotatingFileHandler',
                    'formatter': 'default',
                    'filename': DEFAULT_LOG_FILE,
                    'backupCount': DEFAULT_LOG_BACKUP_COUNT,
                    'maxBytes': DEFAULT_LOG_SIZE
                }
            },
            'loggers': {
                'grbackup': {
                    'handlers': ['default'],
                    'level': 'INFO'
                }
            }
        }
    }
    # Setup argument parser
    argp = argparse.ArgumentParser(description='Gentoo rsync differential backup')
    argp.add_argument(
        '--config',
        '-c',
        action='store',
        type=file,
        default=DEFAULT_CONFIG_FILE,
        help='path to config file'
    )
    argp.add_argument(
        '--version',
        '-V',
        action=Version,
        nargs=0,
        help='Display version'
    )
    argp.add_argument(
        '--log-level',
        '-L',
        action='store',
        default='INFO',
        choices=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'),
        help='Set log level (default INFO)'
    )
    argp.add_argument(
        '--log-file',
        '-l',
        action='store',
        default=DEFAULT_LOG_FILE,
        help='Set log file'
    )
    # Parse arguments
    args = argp.parse_args(sys.argv[1:])
    # Load configuration
    config['logging']['loggers']['grbackup']['level'] = args.log_level
    config['logging']['handlers']['default']['filename'] = args.log_file
    logging.config.dictConfig(config['logging'])
    config = list(yaml.load_all(args.config))
    args.config.close()
    # Start
    log = logging.getLogger('grbackup.main')
    log.info('Grbackup version %s started' % _version)
    # Do backup
    try:
        if not config:
            raise RuntimeError('Empty configuration file')
        Backup(config[0])
    except:
        log.exception(sys.exc_info()[2])
        print 'ERROR:', sys.exc_info()[1]
        print 'See log file for more details'
    log.info('Terminating')
    return 0