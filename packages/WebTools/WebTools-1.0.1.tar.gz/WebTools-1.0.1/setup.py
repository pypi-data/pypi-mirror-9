#!/usr/bin/python
# -*- coding: utf-8 -*-

from setuptools import setup

#<----------------------------------------------------------------------------->

setup(
    name='WebTools',
    version='1.0.1',
    description='Web application development framework',
    url='https://github.com/bourqujl/webtools',
    packages=['webtools', 'webtools.utils'],
    install_requires=['WebOb>=1.4'],
)