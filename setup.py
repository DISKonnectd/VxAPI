#!/usr/bin/env python

from setuptools import setup

packages = [
    'vx_api',
    'vx_api.api_classes',
    'vx_api.cli_classes',
]

requires = [
    'requests',
    'colorama'
]

setup(
    name='requests',
    version='1',
    description='Python HTTP for Humans.',
    author='Kenneth Reitz',
    author_email='me@kennethreitz.com',
    url='http://python-requests.org',
    packages=packages,
    # package_data={'': ['LICENSE', 'NOTICE'], 'requests': ['*.pem']},
    # package_dir={'requests': 'requests'},
    # include_package_data=True,
    install_requires=requires,
    license='Apache 2.0',
)