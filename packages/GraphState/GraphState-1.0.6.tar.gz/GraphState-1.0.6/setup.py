#!/usr/bin/python
# -*- coding: utf8
from distutils.core import setup

setup(
    name='GraphState',
    version='1.0.6',
    author='D. Batkovich, S. Novikov',
    author_email='batya239@gmail.com, dr.snov@gmail.com',
    packages=['graph_state', 'nickel'],
    url='http://pypi.python.org/pypi/GraphState/',
    license='LICENSE.txt',
    description='Graph library implementation using generalization of B.G.Nickel et al. algorithm for identifying graphs.',
    long_description=open('README.txt').read(),
)
