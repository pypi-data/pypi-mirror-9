#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.excutils',
  description = 'Convenience facilities for managing exceptions.',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150110',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.excutils'],
)
