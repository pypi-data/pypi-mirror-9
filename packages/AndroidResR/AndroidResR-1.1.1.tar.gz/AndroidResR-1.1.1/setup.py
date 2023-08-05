#!/usr/bin/env python
# coding=utf-8

from setuptools import find_packages, setup

setup(
    name='AndroidResR',
    version='1.1.1',
    description='A resource manager for Android',
    author='Victor Häggqvist',
    author_email='victor@hggqvst.com',
    url='https://victorhqggqvsit.com',
    license='GPLv2',
    packages=find_packages(),
    entry_points = {
        'gui_scripts': [
            'AndroidResR = AndroidResR.AndroidResR:main'
        ]
    },
    download_url = "https://github.com/victorhaggqvist/AndroidResR/tarball/1.0.1"
)
