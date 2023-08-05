#!/usr/bin/env python

from os.path import exists
from setuptools import setup, find_packages

setup(name='into',
      version='0.1.4',
      description='Data migration utilities',
      url='http://github.com/ContinuumIO/into/',
      author='Matthew Rocklin',
      author_email='mrocklin@continuum.io',
      license='BSD',
      keywords='into data conversion hdf5 sql blaze',
      packages=find_packages(),
      install_requires=list(open('requirements.txt').read().strip().split('\n')),
      long_description=(open('README.rst').read() if exists('README.rst')
                        else ''),
      zip_safe=False)
