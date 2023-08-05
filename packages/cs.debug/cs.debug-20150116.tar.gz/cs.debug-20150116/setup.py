#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.debug',
  description = 'assorted debugging facilities',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150116',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'Assorted debugging facilities.\n==============================\n\n* Lock, RLock, Thread: wrappers for threading facilties; simply import from here instead of there\n\n* thread_dump, stack_dump: dump thread and stack state\n\n* @DEBUG: decorator to wrap functions in timing and value debuggers\n\n* @trace: decorator to report call and return from functions\n\n* @trace_caller: decorator to report caller of function\n\n* TracingObject: subclass of cs.obj.Proxy that reports attribute use\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.debug'],
  requires = ['cs.py3', 'cs.py.stack', 'cs.logutils', 'cs.obj', 'cs.seq', 'cs.timeutils'],
)
