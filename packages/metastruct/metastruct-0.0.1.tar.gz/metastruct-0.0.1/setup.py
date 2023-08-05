#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
  name='metastruct',
  version='0.0.1',
  description="Just another library.",
  author='Stephen Holsapple',
  author_email='sholsapp@gmail.com',
  url='https://github.com/sholsapp/metastruct',
  packages=find_packages(),
  install_requires=[],
  tests_require=[
    'pytest',
  ],
)
