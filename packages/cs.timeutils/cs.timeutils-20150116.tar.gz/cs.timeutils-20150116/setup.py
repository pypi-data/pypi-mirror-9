#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.timeutils',
  description = 'convenience routines for times and timing',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150116',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'Convenience routines for times and timing.\n------------------------------------------\n\n* sleep(); time.sleep observed to sleep less time than requested, thus this wrapper which will sleep again if necessary\n\n* ISOtime(), time_from_ISO(), tm_from_ISO(): prepackaged recipes for simple convesrions not presented directly by the datetime module\n\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.timeutils'],
)
