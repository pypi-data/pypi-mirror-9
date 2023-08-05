#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='unittest2canopsis',
    version='0.2',
    license='MIT',

    author='David Delassus',
    author_email='david.jose.delassus@gmail.com',
    description='Canopsis Connector which generate events from unittest',
    url='https://github.com/linkdd/unittest2canopsis',
    download_url='https://github.com/linkdd/unittest2canopsis/tarball/0.1',
    keywords=['canopsis', 'unittest'],
    classifiers=[],

    scripts=['scripts/unittest2canopsis'],
    packages=find_packages(),
    install_requires=[
        'argparse>=1.2.1',
        'kombu>=3.0.21'
    ]
)
