#!/usr/bin/env python
from distutils.core import setup
from setuptools import find_packages


setup(
    name='ajenti-dev-multitool',
    version='0.14',
    install_requires=[
        'pyyaml',
    ],
    description='-',
    author='Eugeny Pankov',
    author_email='e@ajenti.org',
    url='http://ajenti.org/',
    scripts=['ajenti-dev-multitool'],
)
