#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name='checkio_docker',
    version='0.0.8',
    description='Build docker images from CheckiO mission module',
    author='CheckiO',
    author_email='igor@checkio.org',
    url='https://github.com/CheckiO/checkio-docker',
    download_url='https://github.com/CheckiO/checkio-docker/tarball/0.0.8',
    packages=find_packages(),
)
