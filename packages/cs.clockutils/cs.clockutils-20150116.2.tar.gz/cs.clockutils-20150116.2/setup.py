#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.clockutils',
  description = 'implementation of PEP0418 with the "Choosing the clock from a list of constraints" get_clock() and get_clocks() functions',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150116.2',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'An implementation of PEP0418 with the "Choosing the clock from a list of constraints" get_clock() and get_clocks() functions.\n=============================================================================================================================\n\nPEP 418 (https://www.python.org/dev/peps/pep-0418/) generated much discussion.\n\nMost particpants wanted a call to get a high resolution monotonic clock, which many platforms offer, and much of the discussion surrounded what guarrentees Python should offer for the clock it returned.\n\nI was of the opinion that:\n\n* the many different clocks available have varying features and that the user should be able to inspect them when handed a clock\n\n* the proposed time.monotonic() et al should be offered as default policies for convenience\n\n* however, the proposed time.monotonic() call and friends represented policy; the user calling it is handed an arbitrary clock with some guarrentees; the user has no facility to implement policy themselves. Therefore I proposed two calls: get_clock() and get_clocks() for requesting or enumerating clocks with desired features from those available on the platform.\n\nThis cs.clockutils package implements get_clock() and get_clocks() and provides example implementations of the "policy" calls such as monotonic().\n\nReferences:\n-----------\n\nPEP418\n  https://www.python.org/dev/peps/pep-0418/\nMy core two posts in the discussion outlining my proposal\n  http://www.mail-archive.com/python-dev@python.org/msg66174.html\n  http://www.mail-archive.com/python-dev@python.org/msg66179.html\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.clockutils'],
)
