#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Setup script for etcd-cli
'''

from setuptools import setup, find_packages
import sys, os, glob

with open('requirements.txt') as f:
    requires = f.read().splitlines()

CLASSIFIERS = [
    'Development Status :: 4 - Beta',
    'Environment :: Console',
    'Intended Audience :: System Administrators',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: Apache Software License',
    'Operating System :: POSIX :: Linux',
    'Operating System :: MacOS :: MacOS X',
    'Programming Language :: Python',
    'Topic :: Database',
]

setup(
    name             = 'etcd-cli',
    version          = '0.1-2',

    description      = 'etcd-cli CLI for Etcd based on schemas per directory',
    long_description = open("README.rst").read(),

    author           = 'Michael Persson',
    author_email     = 'michael.ake.persson@gmail.com',
    url              = 'https://github.com/mickep76/etcd-cli.git',
    license          = 'Apache License, Version 2.0',

    packages         = find_packages(),
    classifiers      = CLASSIFIERS,
    scripts          = ['scripts/etcd-cli'],
    data_files	     = [('/etc/etcd-cli', ['etc/etcd-cli.conf']),
                        ('/etc/etcd-cli/schemas', glob.glob('schemas/*.yaml')),
                        ('/etc/etcd-cli/templates', glob.glob('templates/*.jinja'))],
    install_requires = requires,
)
