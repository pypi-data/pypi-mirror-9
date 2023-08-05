#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages

import os

__requires = filter(None, open('requirements.txt').read().splitlines())

setup(
    name='ajenti.plugin.dashboard',
    version='0.3',
    install_requires=__requires,
    description='Ajenti dashboard plugin',
    author='Ajenti project',
    author_email='e@ajenti.org',
    url='http://ajenti.org',
    packages=find_packages(),
    include_package_data=True,
)
    