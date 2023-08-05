#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

setup(

    name = 'call_seq_browser',
    version = '0.0.1',
    description = 'call sequence visualization',

    author = 'ya790206',
    url = 'https://github.com/ya790206/call_seq_browser',
    license = 'Apache License Version 2.0',
    platforms = 'any',
    classifiers = [
    ],

    packages = find_packages(),

    entry_points = {
    },

    install_requires = ['PySide==1.2.2', 'pyqode.core==1.3.2', 'pyqode.python==1.3.2']

)
