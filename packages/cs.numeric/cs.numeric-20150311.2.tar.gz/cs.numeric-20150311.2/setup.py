#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.numeric',
  description = 'some numeric functions; currently primes() and factors()',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150311.2',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Development Status :: 6 - Mature', 'Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'Numeric functions.\n==================\n\nNumeric functions that do not below to other topics.\n\n* primes: generator yielding the primes in order, starting from 2\n\n* factors: generator yielding the prime factors of a value\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.numeric'],
)
