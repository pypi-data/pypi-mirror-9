#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
from setuptools import setup, find_packages

from fabutils import __author__, __version__


setup(
    name='vo-fabutils',
    author=__author__,
    version=__version__,
    description=('Utilities for creating fabric tasks that deals with '
                 'Vagrant, Django, and more.'),
    long_description=open(os.path.realpath(os.path.join(
        os.path.dirname(__file__), 'README.rst'))).read(),
    author_email='desarrollo@vincoorbis.com',
    install_requires=[
        'fabric >= 1.10'
    ],
    packages=find_packages(),
    include_package_data=True,
    classifiers = [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities'
    ]
)
