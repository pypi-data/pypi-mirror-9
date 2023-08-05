#!/usr/bin/env python

from distutils.core import setup
from setuptools import setup, find_packages

setup(version='0.11',
      description='Scala source analysis tools from foursquare',
      author='Benjy W',
      author_email='benjy@foursquare.com',
      url='https://www.python.org/sigs/distutils-sig/',
      name = 'scala-source-tools',
      packages = find_packages(),
      scripts = ['scripts/scala_import_sorter.py', 'scripts/git-fix-scala-imports.sh']
     )
