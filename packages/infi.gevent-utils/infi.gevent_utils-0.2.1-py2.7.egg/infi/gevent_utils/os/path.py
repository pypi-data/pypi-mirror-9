"""
This module acts as a replacement to some of Python's `os.path` module where the blocking operations are done in a
gevent-friendly manner.
"""
from __future__ import absolute_import
from os import path as _path
from ..deferred import create_threadpool_executed_func

CONSTS = ['altsep', 'extsep', 'pardir', 'pathsep', 'sep', 'supports_unicode_filenames']


DEFERRED_FUNCTIONS = [
    'abspath', 'exists', 'getatime', 'getctime', 'getmtime', 'getsize', 'isdir', 'isfile', 'islink', 'ismount',
    'lexists', 'realpath', 'samefile', 'sameopenfile', 'samestat', 'walk'
]

PASSTHROUGH_FUNCTIONS = [
    'basename', 'commonprefix', 'dirname', 'expanduser', 'expandvars', 'isabs', 'join', 'normcase', 'normpath', 'split',
    'splitdrive', 'splitext', 'relpath'
]


module = globals()
for name in DEFERRED_FUNCTIONS:
    if name in _path.__dict__:
        module[name] = create_threadpool_executed_func(_path.__dict__[name])
for name in CONSTS + PASSTHROUGH_FUNCTIONS:
    if name in _path.__dict__:
        module[name] = _path.__dict__[name]
