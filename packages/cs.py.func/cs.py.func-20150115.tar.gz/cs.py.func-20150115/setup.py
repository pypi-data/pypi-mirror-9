#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.py.func',
  description = 'convenience facilities related to Python functions',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150115',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u"Convenience facilities related to Python functions.\n===================================================\n\nfuncname(func)\n--------------\n\nReturns a string to name `func`. I use this instead of func.__name__ because several things do not have a .__name__. It tries to use .__name__, but falls back to ..__str__().\n\n@derived_property\n-----------------\n\nDecorator for property functions which must be recomputed if another property is updated.\n\n@derived_from(property_name)\n----------------------------\n\nConvenience wrapper of derived_property which names the parent property.\n\n@returns_type(func, basetype)\n-----------------------------\n\nBasis for decorators to do type checking of function return values. Example::\n\n  def returns_bool(func):\n    ''' Decorator for functions which should return Booleans.\n    '''\n    return returns_type(func, bool)\n\n  @returns_bool\n  def f(x):\n    return x == 1\n\nThis has been used for debugging functions called far from their definitions.\n",
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.py.func'],
  requires = ['cs.excutils'],
)
