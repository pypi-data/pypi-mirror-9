#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.py3',
  description = 'Aids for code sharing between python2 and python3.',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150120',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'Python3 helpers to aid code sharing between python2 and python3.\n----------------------------------------------------------------\n\nPresents various names in python 3 flavour for common use in python 2 and python 3.\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.py3'],
)
