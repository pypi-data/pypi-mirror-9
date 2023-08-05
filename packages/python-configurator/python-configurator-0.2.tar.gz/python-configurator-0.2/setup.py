#!/usr/bin/env python3

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name = 'python-configurator',
    version = '0.2',
    description = 'Python module for reading configuration files in different formats',
    long_description = open('README.rst').read() + '\n' + open('CHANGES.rst').read(),
    author = 'GNU Knight',
    author_email = 'idxxx23@gmail.com',
    url = 'https://github.com/idxxx23/configurator',
    packages = ['configurator'],
    classifiers = [ # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Topic :: Software Development',
    ],
)
