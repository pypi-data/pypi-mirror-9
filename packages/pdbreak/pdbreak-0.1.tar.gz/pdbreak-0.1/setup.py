#!/usr/bin/env python
# coding=utf-8

import os
import sys

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


from setuptools import find_packages


if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

setup(
    name='pdbreak',
    version='0.1',
    description='A quick break to your python script',
    long_description=open('README.rst').read(),
    author='Liu Yicong',
    author_email='imyikong@gmail.com',
    packages=find_packages(),
    install_requires=(),
    license='BSD',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
    ],
)
