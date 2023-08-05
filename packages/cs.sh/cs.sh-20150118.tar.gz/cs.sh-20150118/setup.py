#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.sh',
  description = 'Convenience functions for constructing shell commands.',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150118',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'Convenience functions for constructing shell commands\n-----------------------------------------------------\n\nFunctions for safely constructing shell command lines from bare strings.\nSomewhat like the inverse of the shlex stdlib module.\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.sh'],
)
