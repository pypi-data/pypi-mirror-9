"""
Almost a drop-in replacement to Python's builtin ``tempfile`` library. It's almosts a drop-in replacement because we
don't implemented ``SpooledTemporaryFile`` and we can't proxy the ``tempdir`` and ``template`` properties here
(no property descriptors for modules).
Instead of brewing some black magic to enable this, we chose the simple approach where if you want to change ``tempdir``
or ``template``, just import Python's ``tempfile`` and set them.
"""

from __future__ import absolute_import

import tempfile as _tempfile
from .os import _FileObjectThreadWithContext
from .deferred import create_threadpool_executed_func


__all__ = ['TemporaryFile', 'NamedTemporaryFile', 'SpooledTemporaryFile', 'mkstemp', 'mkdtemp', 'mktemp',
           'gettempdir', 'gettempprefix']


_TemporaryFile = create_threadpool_executed_func(_tempfile.TemporaryFile)


def TemporaryFile(mode="w+b", bufsize=-1, *args):
    f = _TemporaryFile(mode, bufsize, *args)
    return _FileObjectThreadWithContext(f, mode, bufsize)


_NamedTemporaryFile = create_threadpool_executed_func(_tempfile.NamedTemporaryFile)


def NamedTemporaryFile(mode="w+b", bufsize=-1, *args):
    f = _NamedTemporaryFile(mode, bufsize, *args)
    result = _FileObjectThreadWithContext(f, mode, bufsize)
    result.name = f.name
    return result


def SpooledTemporaryFile(*args):
    raise NotImplementedError()


mkstemp = create_threadpool_executed_func(_tempfile.mkstemp)
mkdtemp = create_threadpool_executed_func(_tempfile.mkdtemp)
mktemp = create_threadpool_executed_func(_tempfile.mktemp)


_gettempdir = create_threadpool_executed_func(_tempfile.gettempdir)


def gettempdir():
    if _tempfile.tempdir is None:
        return _gettempdir()
    return _tempfile.tempdir

gettempprefix = _tempfile.gettempprefix
