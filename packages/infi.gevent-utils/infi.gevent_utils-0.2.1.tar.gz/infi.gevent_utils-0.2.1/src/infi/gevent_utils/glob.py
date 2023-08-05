"""
This module acts as a drop-in replacement to Python's `glob` module where the blocking operations are done in a
gevent-friendly manner.
"""
from __future__ import absolute_import
import glob as _glob
from .deferred import create_threadpool_executed_func

__all__ = ['glob', 'iglob']

glob = create_threadpool_executed_func(_glob.glob)
iglob = create_threadpool_executed_func(_glob.iglob)
