#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.ansi_colour',
  description = 'Convenience functions for ANSI terminal colour sequences.',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150112',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Development Status :: 6 - Mature', 'Environment :: Console', 'Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'Convenience functions for ANSI terminal colour sequences\n--------------------------------------------------------\n\nMapping and function for adding ANSI terminal colour escape sequences\nto strings for colour highlighting of output.\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.ansi_colour'],
)
