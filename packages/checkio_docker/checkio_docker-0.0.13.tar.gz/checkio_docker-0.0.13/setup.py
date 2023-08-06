#!/usr/bin/env python
from os.path import abspath, dirname, join
from setuptools import setup, find_packages


source_directory = dirname(abspath(__file__))
requirements = [l.strip() for l in open(join(source_directory, 'requirements.txt'))]

setup(
    name='checkio_docker',
    version='0.0.13',
    description='Build docker images from CheckiO mission module',
    author='CheckiO',
    author_email='igor@checkio.org',
    url='https://github.com/CheckiO/checkio-docker',
    download_url='https://github.com/CheckiO/checkio-docker/tarball/0.0.13',
    packages=find_packages(),
    install_requires=requirements,
)
