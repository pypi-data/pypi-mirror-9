#!/usr/bin/python
from distutils.core import setup
setup(
  name = 'cs.queues',
  description = 'some Queue subclasses and ducktypes',
  author = 'Cameron Simpson',
  author_email = 'cs@zip.com.au',
  version = '20150115',
  url = 'https://bitbucket.org/cameron_simpson/css/commits/all',
  classifiers = ['Programming Language :: Python', 'Programming Language :: Python :: 2', 'Programming Language :: Python :: 3', 'Topic :: Software Development :: Libraries :: Python Modules', 'Operating System :: OS Independent', 'Development Status :: 4 - Beta', 'License :: OSI Approved :: GNU General Public License v3 (GPLv3)', 'Intended Audience :: Developers'],
  keywords = ['python2', 'python3'],
  long_description = u'Queue subclasses and ducktypes.\n-------------------------------\n\nPresents:\n\n* IterableQueue and IterablePriorityQueue, Queues with the iterator protocol instead of .get(). Prospective users should also consider iter(Queue.get,sentinel), which plainly I did not.\n\n* Channel, a zero storage message passing object.\n\n* NullQueue, a .puttable object that discards its inputs.\n\n* TimerQueue, a queue for submtting jobs to run at specific times without creating many Timer threads.\n\n* PushQueue, a Queue ducktype which queues a function on .put, whose iterable result is put onto an output Queue.\n',
  package_dir = {'': 'lib/python'},
  py_modules = ['cs.queues'],
  requires = ['cs.debug', 'cs.logutils', 'cs.resources', 'cs.seq', 'cs.py3', 'cs.obj'],
)
