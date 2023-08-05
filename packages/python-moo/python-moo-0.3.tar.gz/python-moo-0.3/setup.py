#!/usr/bin/env python3

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name = 'python-moo',
    version = '0.3',
    description = 'Easy way how to run the same query in multiple SQL databases',
    long_description = open('README.rst').read() + '\n' + open('CHANGES.rst').read(),
    author = 'GNU Knight',
    author_email = 'idxxx23@gmail.com',
    url = 'https://github.com/idxxx23/moo',
    packages = ['moo'],
    classifiers = [ # https://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Programming Language :: Python :: 3',
        'Programming Language :: Python',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Database',
        'Topic :: Software Development',
        'Topic :: System',
    ],
)
