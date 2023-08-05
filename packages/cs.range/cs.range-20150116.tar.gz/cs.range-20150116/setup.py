#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.range',
  description = 'a Range class implementing compact integer ranges with a set-like API, and associated functions',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150116',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'Compact integer ranges with a set-like API\n==========================================\n\nA Range is used to represent integer ranges, such a file offset spans.\n\nMuch of the set API is presented to modify and test Ranges, looking somewhat like sets of intergers but extended slightly to accept ranges as well as individual integers so that one may say "R.add(start, end)" and so forth.\n\nAlso provided:\n\n* Span, a simple start:end range.\n\n* overlap: return the overlap of two Spans\n\n* spans: return an iterable of Spans for all contiguous sequences in the ordered integers supplied\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.range'],
  requires = ['cs.logutils'],
)
