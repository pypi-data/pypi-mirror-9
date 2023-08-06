#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import metrics

setup(
    name='django_metrics',
    version=metrics.__version__,
    packages=find_packages(),
    author='Antoine Humeau',
    author_email='humeau.antoine@gmail.com',
    description='Basic Django app that provides an interface to add metrics code snippets from the Django admin.',
    long_description=open('README.md').read(),
    install_requires=['Django==1.7'],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "Natural Language :: English",
        "Operating System :: OS Independent",
    ],
    license="WTFPL"
)
