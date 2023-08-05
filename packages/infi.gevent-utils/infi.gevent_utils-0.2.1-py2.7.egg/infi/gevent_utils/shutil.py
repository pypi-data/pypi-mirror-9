"""
This module acts as a replacement to some of Python's `shutil` module where the blocking operations are done in a
gevent-friendly manner.
"""
from __future__ import absolute_import
import shutil as _shutil
from .deferred import create_threadpool_executed_func

CONSTS = ['Error']


DEFERRED_FUNCTIONS = [
    'copyfile',
    'copyfileobj',
    'copymode',
    'copystat',
    'copy',
    'copy2',
    'copytree',
    'move',
    'rmtree'
]


PASSTHROUGH_FUNCTIONS = [
    'ignore_patterns'
]


__all__ = CONSTS + DEFERRED_FUNCTIONS + PASSTHROUGH_FUNCTIONS

module = globals()
for name in DEFERRED_FUNCTIONS:
    if name in _shutil.__dict__:
        module[name] = create_threadpool_executed_func(_shutil.__dict__[name])
for name in CONSTS + PASSTHROUGH_FUNCTIONS:
    if name in _shutil.__dict__:
        module[name] = _shutil.__dict__[name]
