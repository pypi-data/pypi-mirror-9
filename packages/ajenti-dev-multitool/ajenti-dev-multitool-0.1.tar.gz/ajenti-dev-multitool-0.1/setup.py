#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages


setup(
    name='ajenti-dev-multitool',
    version='0.1',
    install_requires=[],
    description='-',
    author='Eugeny Pankov',
    author_email='e@ajenti.org',
    url='http://ajenti.org/',
    modules=['ajentidevmultitool'],
    scripts=['ajenti-dev-multitool'],
)
