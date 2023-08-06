#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Setup script for peekaboo
'''

from setuptools import setup, find_packages
import sys, os, glob

with open('requirements.txt') as f:
    requires = f.read().splitlines()

CLASSIFIERS = [
    'Development Status :: 5 - Production/Stable',
    'Environment :: Console',
    'Intended Audience :: System Administrators',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: POSIX :: Linux',
]

setup(
    name             = 'peekaboo',
    version          = '0.7-1',

    description      = 'Expose hardware info through HTTP',
    long_description = open("README.rst").read(),

    author           = 'Michael Persson',
    author_email     = 'michael.ake.persson@gmail.com',
    url              = 'https://github.com/mickep76/peekaboo.git',
    license          = 'Apache License, Version 2.0',

    packages         = find_packages(),
    classifiers      = CLASSIFIERS,
    scripts          = ['scripts/peekaboo'],
    data_files	     = [('/etc', ['etc/peekaboo.conf']),
                        ('/var/lib/peekaboo/plugins/info', glob.glob('plugins/info/*.py')),
                        ('/var/lib/peekaboo/plugins/status', glob.glob('plugins/status/*.py')),
			('/usr/share/peekaboo', ['LICENSE', 'README.rst']),
			('/usr/share/peekaboo/contrib', glob.glob('contrib/*'))],
    install_requires = requires,
)
