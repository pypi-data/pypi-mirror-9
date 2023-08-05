#!/usr/bin/env python2.7

from setuptools import setup

description = '''Adds a command to setup.py for displaying metadata about the package.'''

with open('README.txt', 'r') as f:
    long_description = f.read()

setup(
    author='Joost Molenaar',
    author_email='j.j.molenaar@gmail.com',
    url='https://github.com/j0057/setuptools-metadata',
    name='setuptools-metadata',
    version='0.1.5',
    description=description,
    long_description=long_description,
    packages=['setuptools_metadata'],
    entry_points={
        'distutils.commands': [
            'metadata = setuptools_metadata:metadata'
        ],
        'distutils.setup_keywords': [
            'custom_metadata = setuptools_metadata:validate_dict'
        ]
    })
