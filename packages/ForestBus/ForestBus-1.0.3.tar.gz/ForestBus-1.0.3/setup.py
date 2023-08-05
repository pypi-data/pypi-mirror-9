#!/usr/bin/env python

import sys, os
sys.path.insert(0, os.path.join(os.getcwd(),'lib'))

from distutils.core import setup

try:
   from distutils.command.build_py import build_py_2to3 as build_py
except ImportError:
   from distutils.command.build_py import build_py

import forestbus

setup(name='ForestBus',
      version=forestbus.__version__,
      description='ForestBus Python Client Library',
      author='Colin Stewart',
      author_email='colin@owlfish.com',
      url='http://www.owlfish.com/software/ForestBus/',
      classifiers=["License :: OSI Approved :: MIT License", "Natural Language :: English","Topic :: Software Development :: Libraries","Topic :: System :: Distributed Computing"],
      packages=['forestbus'],
      package_dir = {'': 'lib'},
      requires=['cbor'],
      cmdclass = {'build_py': build_py},
     )

