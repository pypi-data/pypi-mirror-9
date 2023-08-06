#!/usr/bin/python

from distutils.core import setup

setup(name='pedees',
      version='0.2',
      description='A simple PDE solver',
      author='Alexander Pletzer',
      author_email='alexander@gokliya.net',
      py_modules=['pedees.delaunay2d', 'pedees.inside', 'pedees.elliptic2dDriver',
                  'pedees.elliptic2d', 'pedees.cg', 'pedees.plot'],
     )
