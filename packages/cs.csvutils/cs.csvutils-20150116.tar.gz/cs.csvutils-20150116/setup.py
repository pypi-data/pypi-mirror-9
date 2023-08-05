#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.csvutils',
  description = 'CSV file related facilities',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150116',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u"CSV file related facilities.\n============================\n\n* csv_reader(fp, encoding='utf-8', errors='replace'): python 2/3 portable interface to CSV file reading. Reads CSV data from the text file `fp` using csv.reader.\n\n* SharedCSVFile: subclass of cs.fileutils.SharedAppendLines, for sharing an append-only CSV file.\n",
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.csvutils'],
  requires = ['cs.fileutils', 'cs.debug', 'cs.logutils', 'cs.queues'],
)
