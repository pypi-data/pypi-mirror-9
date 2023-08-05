#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.threads',
  description = 'threading and communication/synchronisation conveniences',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150115',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'Threading and communication/synchronisation conveniences.\n=========================================================\n\nNotably:\n\n* WorkerThreadPool, a pool of worker threads to run functions.\n\n* AdjustableSemaphore, a semaphore whose value may be tuned after instantiation.\n\n* @locked, decorator for object methods which should hold self._lock\n\n* @locked_property, a thread safe caching property\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.threads'],
  requires = ['cs.seq', 'cs.excutils', 'cs.debug', 'cs.logutils', 'cs.obj', 'cs.queues', 'cs.py.func', 'cs.py3'],
)
