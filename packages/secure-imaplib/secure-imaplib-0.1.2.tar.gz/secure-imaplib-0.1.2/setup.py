#!/usr/bin/env python
from ez_setup import use_setuptools
use_setuptools("0.7.0")

from setuptools import setup, find_packages

readme = open('README.rst').read()
history = open('CHANGES.rst').read().replace('.. :changelog:', '')

setup(
    name='secure-imaplib',
    version='0.1.2',
    author='Thomas Grainger',
    author_email='secure-imaplib@graingert.co.uk',
    maintainer='Thomas Grainger',
    maintainer_email = 'secure-imaplib@graingert.co.uk',
    keywords = 'imaplib, TLS, SSL, verify, validate, ca_cert, ca',
    description = 'Secure IMAP subclasses for Python 2',
    long_description=readme + '\n\n' + history,
    url='https://github.com/graingert/secure-imaplib',
    package_dir={'': 'src'},
    packages=find_packages('src', exclude="tests"),
    zip_safe=True,
    include_package_data=False,
)
