#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.obj',
  description = 'Convenience facilities for objects.',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150118',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'Convenience facilities for objects.\n-----------------------------------\n\nPresents:\n* flavour, for deciding whether an object resembles a mapping or sequence.\n\n* O, an object subclass with a nice __str__ and convenient __init__.\n\n* Some O_* functions for working with objects, particularly O subclasses.\n\n* Proxy, a very simple minded object proxy intened to aid debugging.\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.obj'],
  requires = ['cs.py3'],
)
