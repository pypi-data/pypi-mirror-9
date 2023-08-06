#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(
    name='django-pluggable',
    description='Testrunner for pluggable apps.',
    version='0.0.1',
    #long_description=open('README.rst').read(),
    author='Anton Agestam',
    author_email='msn@antonagestam.se',
    packages=find_packages(),
    url='https://github.com/antonagestam/django-pluggable/',
    license='The MIT License (MIT)',
    install_requires=['Django>=1.7.5', 'click>=3.3', ],
    scripts=['runtests.py'],
    classifiers=['Programming Language :: Python :: 2.7',
                 'Programming Language :: Python :: 3']

)
