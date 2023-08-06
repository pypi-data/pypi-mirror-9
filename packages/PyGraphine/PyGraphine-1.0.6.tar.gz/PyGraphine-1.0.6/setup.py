#!/usr/bin/python
# -*- coding: utf8
from distutils.core import setup

setup(
    name='PyGraphine',
    version='1.0.6',
    author='D. Batkovich',
    author_email='batya239@gmail.com',
    packages=['graphine', 'graphine.test'],
    url='http://pypi.python.org/pypi/PyGraphine/',
    license='LICENSE.txt',
    description='Graph manipulation package based on GraphState',
    long_description=open('README.txt').read(),
    requires=['GraphState (>= 1.0.2)']
)
