#!/usr/bin/env python

from distutils.core import setup
from setuptools import setup, find_packages

setup(version='0.12',
      description='Stupid pants utils',
      author='David Blackman',
      author_email='david@blackmad.com',
      url='https://www.python.org/sigs/distutils-sig/',
      name = 'pants-build-utils',
      packages = find_packages(),
      entry_points = {
        'console_scripts': [
          'pants-smart-compile = pants.smart_compile:compile_main',
          'pants-smart-test= pants.smart_compile:test_main',
        ]
      }
     )
