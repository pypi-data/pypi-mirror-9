#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.later',
  description = 'queue functions for execution later',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150115',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'Later: queue functions for execution later in priority and time order.\n======================================================================\n\nI use Later objects for convenient queuing of functions whose execution occurs later in a priority order with capacity constraints.\n\nWhy not futures? I already had this, I prefer its naming scheme and interface, and futures did not seem to support prioritising execution.\n\nUse is simple enough: create a Later instance and typically queue functions with the .defer() method::\n\n  L = Later(4)      # a Later with a parallelism of 4\n  ...\n  LF = L.defer(func, *args, **kwargs)\n  ...\n  x = LF()          # collect result\n\nThe .defer method and its sublings return a LateFunction, which is a subclass of cs.asynchron.Asynchron. As such it is a callable, so to collect the result you just call the LateFunction.\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.later'],
  requires = ['cs.py3', 'cs.py.func', 'cs.debug', 'cs.excutils', 'cs.queues', 'cs.threads', 'cs.asynchron', 'cs.seq', 'cs.logutils'],
)
