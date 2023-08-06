#!/usr/bin/env python

from distutils.core import setup

setup(
    name='PyHubble',
    version='0.1.0',
    author='Javier Aguirre',
    author_email='hello@javaguirre.net',
    packages=['pyhubble'],
    url='https://github.com/javaguirre/pyhubble',
    license=open('LICENSE.txt').read(),
    description='A python client for hubble',
    long_description='',
    install_requires=['requests'],
    keywords=['hubble']
)
