#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.tty',
  description = 'functions related to terminals',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150116',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Terminals', 'Operating System :: POSIX', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'Functions related to terminals.\n===============================\n\n* ttysize(fd): return a namedtuple (rows, columns) with the current terminal size; UNIX only (uses the stty command)\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.tty'],
)
