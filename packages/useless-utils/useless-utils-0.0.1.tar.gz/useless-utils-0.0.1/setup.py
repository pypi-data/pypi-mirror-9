#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# @file     setup.py  
# @author   kaka_ace <xiang.ace@gmail.com>
# @date     Mar 08 2015
# @breif     
# 


from setuptools import setup, find_packages
import sys, os

version = '0.0.1'


requires = [
   "pycrypto",
]


kwargs = {}
with open("README.md", 'r') as f:
    kwargs['long_description'] = f.read()


setup(
    name='useless-utils',
    version=version,
    description= "useless utils function class generator etc. (using Python3)",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: Implementation :: CPython",
    ], # Get strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
    keywords='useless utils',
    author='kaka_ace',
    author_email='xiang.ace@gmail.com',
    url='http://kaka-ace.com',
    license='http://opensource.org/licenses/MIT',
    #packages=find_packages(exclude=['ez_setup', 'examples', 'tests', "demos"]),
    packages=["useless_utils",],
    include_package_data=True,
    zip_safe=True,
    install_requires=requires,
    entry_points="""
        # -*- Entry points: -*-
    """,
    **kwargs
)
      
