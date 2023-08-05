#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.configutils',
  description = 'utility functions for .ini style configuration files',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150118',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'Configuration file utility functions.\n=====================================\n\nClasses:\n\nConfigWatcher\n-------------\n\nA monitor for a .ini style configuration file, allowing outside users to update the file on the fly. It presents a mapping interface of section names to ConfigSectionWatcher instances, and a .config property returning the current ConfigParser instance.\n\nConfigSectionWatcher\n--------------------\n\nA monitor for a section of a .ini style configuration file, allowing outside users to update the file on the fly. It presents a mapping interface of section field names to values.\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.configutils'],
  requires = ['cs.py3', 'cs.fileutils', 'cs.threads', 'cs.logutils'],
)
