# -*- coding: utf-8 -*-

import argument
from setuptools import setup, find_packages


with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()


setup(
    name='argument',
    version=argument.version,
    description='Command line argument parsing library for python',
    long_description=readme,
    author='oskarnyqvist',
    author_email='oskarnyqvist@gmail.com',
    url='https://github.com/oskarnyqvists/arguments',
    license=license,
    packages=find_packages(exclude=('tests', 'docs')),
)
