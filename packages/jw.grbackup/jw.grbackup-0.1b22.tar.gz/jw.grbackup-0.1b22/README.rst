grbackup
========

Introduction
------------

This is a simple backup script for use exclusively under Gentoo Linux. It uses the repository of system-installed files
to automatically exclude them from backup because those files can (and should) be reinstalled easily with the *portage*
package manager.

Configuration
-------------

Grbackup uses a configuration file (``~/.local/etc/grbackup`` if not overridden on the command line) for its required
information in order to be run with a simple command for daily use. The configuration file is in the
`YAML <http://www.yaml.org>`_ format. The format is simple enough to be described by an example::

    roots:
        - /
    prune:
        - /tmp
        - /proc
        - /sys
        - /dev
        - /mnt
        - /var/tmp
        - /var/run
        - /var/cache
        - /run
        - /lost+found
    destination:
        user: backup
        host: backuphost
        port: 22
        directory: /backup/{HOSTNAME}/rsync-backup
        generations: 7

There are three sections (*root*, *prune* and *destination*). In the *root* section, a list of directories to be
included in the backup are stated. Each list element is on a separate line and begins with "- " (the space after the
dash is required).

The *prune* section contains a list of directories to be excluded from the backup.

In the *destination* section, a couple of parameters specify where the backup has to be written to. Since *rsync* is
capable of writing to remote hosts through the use of *ssh*, three parameters, *user*, *host* and *port* specify the
necessary information for reaching a remote host. As of version 0.1b, the *host* parameter is required, meaning only
remote backups are possible. This will change in later versions, allowing local backups. The parameter *directory*
specifies the base destination directory on the remote host. As you can see in the example, there can be variable
substitution expressions in the form of ``{VARIABLE}``. The expression will be replaced by the respective environment
variable. The parameter *generations* specifies how many generations of old backups are to be retained before they are
removed. The default is 30.

Backup organisation
-------------------

To enable differential backups, the backup is stored under a subdirectory of the destination directory specified in the
*destination* section of the configuration. This subdirectory has a name resembling a time stamp with date and time,
like ``2014-02-12-03:12:26`` where the first three numbers are the date in ISO-format and the last three numbers are the
time in 24-hour-format.

The new backup is stored in reference to the last backup. All changed files are stored normally. Files which have
not changed since the last backup are simply hard-linked to the corresponding file in the old backup. This way they
don't take any addition space on the backup medium (apart from the directory entry). This is done by *rsync* by the
use of the ``--link-dest`` option.

Usage
-----

The program is intended to be run by the simple command::

    grbackup

There are some options for testing and one-time use:


    -h, --help                      shows a help message and exits
    --config file, -c file          to specify the path to an alternative configuration file (default: ~/.grbackup)
    --version, -V                   displays the program version
    --log-level level, -L level     to set the log level. Level is one of DEBUG, INFO, WARNING, ERROR, or
                                    CRITICAL. DEBUG shows the most detail while CRITICAL shows almost nothing.
                                    (default: INFO)
    --log-file file, -l file        to set log file (default: /var/log/grbackup)

Installation
------------

The software can be installed easily from the Python software repository, either on the command line or by downloading
the package and installing it explicitly.

.. note::

   Python packages **must not** be installed using *pip* or *easy_install* globally in the system environment under
   Gentoo Linux. There is a carefully crafted system to make system-provided Python scripts available under Python 2 as
   well as Python 3 which is disturbed by packagages deliberately installed by *pip* or *easy_install*. Since
   backups are done almost always by *root*, the software should be installed in *root*'s home directory, ``/root``.
   This is done with *pip*'s ``--user`` switch. Another way is to use *pip*'s ``--root`` option and adjust
   ``PYTHONPATH``.

Installation using *pip*
~~~~~~~~~~~~~~~~~~~~~~~~

On the command line, type::

    pip install --user jw.grbackup

Explicit Installation from a downloaded package
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Download the package from https://pypi.python.org/pypi/jw.grbackup. Unpack it, ``cd`` into the unpacked directory and
type the command::

    python setup.py install --user

Installation problems
~~~~~~~~~~~~~~~~~~~~~

If you have never installed a Python package before, chances are your version of *setuptools* is outdated. Normally,
packages and their dependencies are updated automatically, but not in the case of *setuptools*, because this is the very
package doing the installation and it can't update itself while it is running, so this needs to be done manually. If
something like the following is displayed when the installation is running::

    The required version of setuptools (>=*something*) is not available,
    and can't be installed while this script is running. Please
    install a more recent version first, using
    'easy_install -U setuptools'.

then just type the command (don't miss to include the ``--user`` flag, it's not mentioned in the error text)::

    easy_install --user -U setuptools

This will install a current version of *setuptools* into your user environment. After that, retry your installation.

Bug reports
-----------

Please report bugs and enhancement requests to https://bitbucket.org/JohnnyWezel/jw.grbackup/issues.