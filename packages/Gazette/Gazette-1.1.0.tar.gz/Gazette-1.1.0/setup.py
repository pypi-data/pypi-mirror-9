#!/usr/bin/env python

"""Setup script for Gazette."""

import setuptools

from gazette import __project__, __version__

import os
if os.path.exists('README.rst'):
    README = open('README.rst').read()
else:
    README = ""  # a placeholder, readme is generated on release
CHANGES = open('CHANGES.md').read()


setuptools.setup(
    name=__project__,
    version=__version__,

    description="A flexible CMS library that can be added into any app.",
    url='https://sf.net/p/gazette',
    author='Gazette Team',

    packages=setuptools.find_packages(),

    entry_points={'console_scripts': []},

    long_description=(README + '\n' + CHANGES),
    license='MIT',
    classifiers=[
        'Natural Language :: English',
        'Operating System :: OS Independent',
    ],

    install_requires=[
        'bottle',
        'jsonpickle',
    ],

    test_suite='nose.collector',
    tests_require=[
        'nose',
        'jinja2',
        'datastore',
        'webtest',
        'datastore.mongo',
    ]
)
