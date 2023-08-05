#!/usr/bin/env python

from setuptools import setup, find_packages

pkgs = find_packages()

setup(
    name='strictdict',
    version='0.4',
    description='Strict Dict',
    author='Dmitry Zhiltsov',
    author_email='dzhiltsov@me.com',
    ext_modules=[],
    packages=pkgs,
    scripts=[],
    data_files=[],
    install_requires=[
        'msgpack-python',
    ],
)
