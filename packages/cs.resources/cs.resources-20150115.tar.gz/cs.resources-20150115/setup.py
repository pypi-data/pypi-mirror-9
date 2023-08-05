#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.resources',
  description = 'resourcing related classes and functions',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150115',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u"Resourcing related classes and functions.\n=========================================\n\nNestingOpenClosedMixin\n----------------------\n\nThis is a mixin class for objects with multiple open/close users.\nAfter the last .close, the object's .shutdown method is called.\nThis also presented the context manager interface to allow open/close thus::\n\n  with obj:\n    do stuff while open\n\n@notclosed\n----------\n\nDecorator for object methods which must not be called after the object is closed.\n",
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.resources'],
  requires = ['cs.excutils', 'cs.logutils', 'cs.obj', 'cs.py.func'],
)
