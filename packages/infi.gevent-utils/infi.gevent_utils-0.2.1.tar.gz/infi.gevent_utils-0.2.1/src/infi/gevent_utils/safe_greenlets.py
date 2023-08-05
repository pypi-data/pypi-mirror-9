import sys
from infi.traceback import traceback_decorator
from infi.pyutils.contexts import contextmanager
import gevent
import gevent.pool
from logbook import Logger
logger = Logger(__name__)

_uncaught_exception_handler = None


class SafeGreenlet(gevent.Greenlet):
    def __init__(self, run, *args, **kwargs):
        super(SafeGreenlet, self).__init__(wrap_uncaught_greenlet_exceptions(run), *args, **kwargs)


class SafePool(gevent.pool.Pool):
    greenlet_class = SafeGreenlet


def set_greenlet_uncaught_exception_handler(func):
    """
    Sets a global greenlet uncaught exception handler that will get called if a greenlet spawned by one of this module's
    wrappers raises an uncaught exception.
    :param func: exception handler function that will receive the exc_info tuple as an argument
    :returns: previous exception handler function or None
    """
    global _uncaught_exception_handler
    prev_handler, _uncaught_exception_handler = _uncaught_exception_handler, func
    return prev_handler


@traceback_decorator
def uncaught_greenlet_exception():
    global _uncaught_exception_handler
    if _uncaught_exception_handler:
        _uncaught_exception_handler()
    else:
        logger.exception("uncaught exception in greenlet and uncaught exception handler was not set, calling sys.exit")
        sys.exit("uncaught greenlet exception")


@contextmanager
def uncaught_greenlet_exception_context():
    try:
        yield
    except gevent.GreenletExit:
        raise
    except:
        uncaught_greenlet_exception()


def _normalize_instancemethod(instance_method):
    """
    wraps(instancemethod) returns a function, not an instancemethod so its repr() is all messed up;
    we want the original repr to show up in the logs, therefore we do this trick
    """
    if not hasattr(instance_method, 'im_self'):
        return instance_method

    def _func(*args, **kwargs):
        return instance_method(*args, **kwargs)

    _func.__name__ = repr(instance_method)
    return _func


def wrap_uncaught_greenlet_exceptions(func):
    def _func(*args, **kwargs):
        with uncaught_greenlet_exception_context():
            return func(*args, **kwargs)
    _func.__name__ = repr(func)
    return _func


def safe_spawn(func, *args, **kwargs):
    return gevent.spawn(wrap_uncaught_greenlet_exceptions(func), *args, **kwargs)


def safe_spawn_later(seconds, func, *args, **kwargs):
    return gevent.spawn_later(seconds, wrap_uncaught_greenlet_exceptions(func), *args, **kwargs)


def safe_spawn_and_switch_immediately(func, *args, **kwargs):
    greenlet = safe_spawn(func, *args, **kwargs)
    gevent.sleep(0)
    return greenlet


def set_hub_error_handlers():
    hub = gevent.get_hub()
    original_hub_system_error = hub.handle_system_error

    def handle_error(context, type, value, tb):
        logger.error("encountered gevent hub error {}: {}".format(type, value))
        # the original function just logs the exceptions to stderr
        if issubclass(type, KeyboardInterrupt):
            original_hub_system_error(type, value)
        else:
            uncaught_greenlet_exception()

    def handle_system_error(type, value):
        # the original function just logs the exceptions to stderr
        logger.error("encountered gevent hub system error {}: {}".format(type, value))
        uncaught_greenlet_exception()

    gevent.get_hub().handle_error = handle_error
    gevent.get_hub().handle_system_error = handle_system_error


def safe_joinall(greenlets, timeout=None, raise_error=False):
    """
    Wrapper for gevent.joinall if the greenlet that waits for the joins is killed, it kills all the greenlets it
    joins for.
    """
    greenlets = list(greenlets)
    try:
        gevent.joinall(greenlets, timeout=timeout, raise_error=raise_error)
    except gevent.GreenletExit:
        [greenlet.kill() for greenlet in greenlets if not greenlet.ready()]
        raise
    return greenlets
