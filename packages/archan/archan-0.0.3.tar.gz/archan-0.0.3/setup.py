#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
from setuptools import setup

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='archan',
    version='0.0.3',
    packages=['archan'],
    license='MPL 2.0',

    author='Pierre Parrend',
    author_email='parrend@unistra.fr',
    url='https://github.com/Pawamoy/archan',
    # download_url = 'https://github.com/Pawamoy/archan/tarball/0.0.1',

    install_requires=['future'],

    keywords="architecture analysis dependency matrix dsm",
    description="A Python module that analyses your architecture strength "
                "based on DSM data.",
    classifiers=[
        # "Development Status :: 5 - Production/Stable",
        'Development Status :: 4 - Beta',
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Topic :: Utilities",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4",
        "License :: OSI Approved :: Mozilla Public License 2.0 (MPL 2.0)",
    ]
)
