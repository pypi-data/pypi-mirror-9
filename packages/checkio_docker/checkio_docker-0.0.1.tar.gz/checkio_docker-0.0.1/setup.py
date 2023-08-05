#!/usr/bin/env python
from setuptools import setup, find_packages


setup(
    name='checkio_docker',
    version='0.0.1',
    description='Build docker images from CheckiO mission module',
    author='CheckiO',
    author_email='igor@checkio.org',
    url='https://github.com/CheckiO/checkio-docker',
    download_url='https://github.com/CheckiO/checkio-docker/tarball/0.1',
    packages=find_packages(),
)
