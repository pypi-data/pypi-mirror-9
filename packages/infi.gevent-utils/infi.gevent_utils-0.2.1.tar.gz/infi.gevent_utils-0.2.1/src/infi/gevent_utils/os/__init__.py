"""
This module acts as an 99% drop-in replacement to Python's `os` module where the blocking operations are done in a
gevent-friendly manner.
When we say "blocking operations" we mean not only the obvious blockers such as read and write, but also other
operations that may trigger I/O such as close, listdir, fstat and the like.
Also, on UNIXes (and Windows through the POSIX module), read and writes from a local file may block even if we enable
O_NONBLOCK. So for them we need also need to defer to a thread.
"""
from __future__ import absolute_import
import os as _os
from gevent.queue import Queue
from gevent.hub import get_hub
from gevent.fileobject import FileObjectThread
from gevent.os import make_nonblocking, nb_read, nb_write
from gevent import fork  # Ignore lint error - it's added to __all__

from ..deferred import create_threadpool_executed_func
from . import path  # Ignore lint error -it's added to __all__

# All os.xxx attributes were extracted from Python 2.7.6 on Ubuntu
CONSTS = [
    'EX_CANTCREAT', 'EX_CONFIG', 'EX_DATAERR', 'EX_IOERR', 'EX_NOHOST', 'EX_NOINPUT', 'EX_NOPERM', 'EX_NOUSER', 'EX_OK',
    'EX_OSERR', 'EX_OSFILE', 'EX_PROTOCOL', 'EX_SOFTWARE', 'EX_TEMPFAIL', 'EX_UNAVAILABLE', 'EX_USAGE', 'F_OK',
    'NGROUPS_MAX', 'O_APPEND', 'O_ASYNC', 'O_CREAT', 'O_DIRECT', 'O_DIRECTORY', 'O_DSYNC', 'O_EXCL', 'O_LARGEFILE',
    'O_NDELAY', 'O_NOATIME', 'O_NOCTTY', 'O_NOFOLLOW', 'O_NONBLOCK', 'O_RDONLY', 'O_RDWR', 'O_RSYNC', 'O_SYNC',
    'O_TRUNC', 'O_WRONLY', 'P_NOWAIT', 'P_NOWAITO', 'P_WAIT', 'R_OK', 'SEEK_CUR', 'SEEK_END', 'SEEK_SET', 'ST_APPEND',
    'ST_MANDLOCK', 'ST_NOATIME', 'ST_NODEV', 'ST_NODIRATIME', 'ST_NOEXEC', 'ST_NOSUID', 'ST_RDONLY', 'ST_RELATIME',
    'ST_SYNCHRONOUS', 'ST_WRITE', 'TMP_MAX', 'WCONTINUED', 'WCOREDUMP', 'WEXITSTATUS', 'WIFCONTINUED', 'WIFEXITED',
    'WIFSIGNALED', 'WIFSTOPPED', 'WNOHANG', 'WSTOPSIG', 'WTERMSIG', 'WUNTRACED', 'W_OK', 'X_OK',
    'altsep', 'curdir', 'defpath', 'devnull', 'environ', 'error', 'extsep', 'linesep', 'name', 'pardir', 'pathsep',
    'sep'
]

PASSTHROUGH_FUNCTIONS = [
    '_exit', 'abort', 'confstr', 'confstr_names', 'ctermid', 'dup', 'dup2', 'execl', 'execle', 'execlp', 'execlpe',
    'execv', 'execve', 'execvp', 'execvpe', 'getcwd', 'getcwdu', 'getegid', 'getenv', 'geteuid', 'getgid', 'getgroups',
    'getloadavg', 'getlogin', 'getpgid', 'getpgrp', 'getpid', 'getppid', 'getresgid', 'getresuid', 'getsid', 'getuid',
    'initgroups', 'kill', 'killpg', 'major', 'makedev', 'minor', 'nice', 'pathconf_names', 'putenv', 'setegid',
    'seteuid', 'setgid', 'setgroups', 'setpgid', 'setpgrp', 'setregid', 'setresgid', 'setresuid', 'setreuid', 'setsid',
    'setuid', 'stat_float_times', 'strerror', 'sysconf', 'sysconf_names', 'tcgetpgrp', 'tcsetpgrp', 'times', 'ttyname',
    'umask', 'uname', 'unsetenv'
]

DEFERRED_FUNCTIONS = [
    'access', 'chdir', 'chflags', 'chmod', 'chown', 'chroot', 'close', 'closerange', 'fchdir', 'fchmod', 'fchown',
    'fdatasync', 'fpathconf', 'fstat', 'fstatvfs', 'fsync', 'ftruncate', 'isatty', 'lchflags', 'lchmod', 'lchown', 'link',
    'listdir', 'lseek', 'lstat', 'makedirs', 'mkdir', 'mkfifo', 'mknod', 'openpty', 'pathconf', 'read', 'readlink', 'remove',
    'removedirs', 'rename', 'renames', 'rmdir', 'spawnl', 'spawnle', 'spawnlp', 'spawnlpe', 'spawnv', 'spawnve',
    'spawnvp', 'spawnvpe', 'stat', 'stat_float_times', 'statvfs', 'symlink', 'system', 'tempnam', 'tmpnam', 'unlink',
    'urandom', 'utime' 'wait', 'wait3', 'wait4', 'waitpid', 'write', 'walk'
]

NOT_IMPLEMENTED_FUNCTIONS = [
    'forkpty', 'pipe', 'popen', 'popen2', 'popen3', 'popen4'
]


__all__ = ['path', 'fopen', 'open', 'read', 'write', 'fork'] + DEFERRED_FUNCTIONS + PASSTHROUGH_FUNCTIONS + CONSTS


class _FileObjectThreadWithContext(FileObjectThread):
    """Adds context manager functionality to gevent's `FileObject`."""
    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        self.close()


_fopen = create_threadpool_executed_func(open)
_fdopen = create_threadpool_executed_func(_os.fdopen)


def fopen(name, mode='r', buffering=-1):
    """Similar to Python's built-in `open()` function."""
    f = _fopen(name, mode, buffering)
    return _FileObjectThreadWithContext(f, mode, buffering)
fopen.__doc__ = open.__doc__


def fdopen(fd, mode='r', buffering=-1):
    f = _fdopen(fd, mode, buffering)
    return _FileObjectThreadWithContext(f, mode, buffering)
fdopen.__doc__ = _os.fdopen.__doc__


_tmpfile = create_threadpool_executed_func(_os.tmpfile)


def tmpfile():
    f = _tmpfile()
    return _FileObjectThreadWithContext(f, "w+b")
tmpfile.__doc__ = _os.tmpfile.__doc__


_open = create_threadpool_executed_func(_os.open)


def open(file, flags, mode=0777):
    fd = _open(file, flags, mode)
    # this is (almost) pointless since local files may block even if we set non-blocking on Linux
    # it's still interesting if the file is a named pipe, UNIX-domain socket, etc.
    make_nonblocking(fd)
    return fd


# Here we convert most of os's file-related functions to functions that are deferred to a thread so they'll be
# gevent-friendly: they still will block, but will release the greenlet so other greenlets can execute.
module = globals()
for name in DEFERRED_FUNCTIONS:
    if name in _os.__dict__:
        module[name] = create_threadpool_executed_func(_os.__dict__[name])
for name in CONSTS + PASSTHROUGH_FUNCTIONS:
    if name in _os.__dict__:
        module[name] = _os.__dict__[name]
for name in NOT_IMPLEMENTED_FUNCTIONS:
    if name in _os.__dict__:
        def _not_implemented(*args, **kwargs):
            raise NotImplementedError()
        _not_implemented.__name__ = name
        module[name] = _not_implemented
