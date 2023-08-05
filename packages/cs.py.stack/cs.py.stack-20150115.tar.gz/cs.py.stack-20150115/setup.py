#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.py.stack',
  description = 'Convenience functions for the python execution stack.',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150115',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u"Convenience functions for the python execution stack.\n-----------------------------------------------------\n\nI find the supplied python traceback facilities quite awkward.\nThese functions provide convenient facilities.\n\nPresented:\n\n* Frame, a nametuple for a stack frome with a nice __str__.\n\n* frames(), returning the current stack as a list of Frames.\n\n* caller(), returning the Frame of the caller's caller.\n",
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.py.stack'],
)
