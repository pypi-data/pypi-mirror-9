#!/usr/bin/env python

from setuptools import setup, find_packages
from assertionchain import __version__

with open("./requirements.txt") as fp:
    requirements = fp.read()
    requirements = requirements.split("\n")

setup(
    name='assertionchain',
    description='Utility for chaining commands and incrementally checking the results',
    version=__version__,
    author='Justin Iso',
    author_email='justin+assertionchain@justiniso.com',
    url='https://github.com/justiniso/assertionchain',
    download_url='https://github.com/justiniso/assertionchain/tarball/0.1.0',
    packages=find_packages(),
    install_requires=requirements,
    test_suite='tests'
)