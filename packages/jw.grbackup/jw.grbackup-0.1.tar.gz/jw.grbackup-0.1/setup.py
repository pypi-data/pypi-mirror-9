#!/usr/bin/env python

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

from setuptools import setup, find_packages
from grbackup import _version

setup(
    name='jw.grbackup',
    version=_version,
    platforms='POSIX',
    url='https://pypi.python.org/pypi/jw.grbackup',
    license='GPL',
    author='Johnny Wezel',
    author_email='dev-jay@wezel.name',
    description='Gentoo rsync backup -- a simple differential backup script for Gentoo Linux',
    long_description=file('README.rst').read(),
    keywords='backup, utility',
    install_requires=[
        'setuptools>=3',
        'PyYAML',
        'blist',
        'paramiko'
    ],
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'grbackup = grbackup.main:Main'
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 2.7',
        'Topic :: System :: Archiving :: Backup',
        'Topic :: System :: Archiving :: Mirroring',
        'Topic :: Utilities'
    ]
)

