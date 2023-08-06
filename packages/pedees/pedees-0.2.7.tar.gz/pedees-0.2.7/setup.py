#!/usr/bin/python

from distutils.core import setup

from pedees._version import __version__
setup(name='pedees',
      version=__version__,
      description='A simple PDE solver',
      author='Alexander Pletzer',
      author_email='alexander@gokliya.net',
      py_modules=['pedees.delaunay2d', 
                  'pedees.inside', 
                  'pedees.elliptic2dDriver',
                  'pedees.elliptic2dDriverBase',
                  'pedees.elliptic2dDriverDiscretePoints',
                  'pedees.elliptic2d', 
                  'pedees.cg', 
                  'pedees.plot',
                  'pedees._version'],
     )
