import gevent
from gevent.event import Event
from infi.pyutils.contexts import contextmanager

from .safe_greenlets import uncaught_greenlet_exception_context


class GeventLoopBase(object):
    """A base class for implementing an operation that sleeps for `interval` between callback executions."""
    def __init__(self, interval):
        super(GeventLoopBase, self).__init__()
        self._interval = interval
        self._stop_event = None
        self._greenlet = None

    def _loop(self):
        """Main loop - used internally."""
        while True:
            try:
                with uncaught_greenlet_exception_context():
                    self._loop_callback()
            except gevent.GreenletExit:
                break
            if self._stop_event.wait(self._interval):
                break
        self._clear()

    def _loop_callback(self):
        """Subclasses should implement this function - called every loop iteration."""
        raise NotImplementedError()  # pragma: nocover

    def start(self):
        """
        Starts the loop. Calling a running loop is an error.
        """
        assert not self.has_started(), "called start() on an active GeventLoop"
        self._stop_event = Event()
        # note that we don't use safe_greenlets.spawn because we take care of it in _loop by ourselves
        self._greenlet = gevent.spawn(self._loop)

    def stop(self, timeout=None):
        """
        Stops a running loop and waits for it to end if timeout is set. Calling a non-running loop is an error.
        :param timeout: time (in seconds) to wait for the loop to end after signalling it. ``None`` is to block till it ends.
        :return: True if the loop stopped, False if still stopping.
        """
        assert self.has_started(), "called stop() on a non-active GeventLoop"
        greenlet = self._greenlet if gevent.getcurrent() != self._greenlet else None
        self._stop_event.set()
        if greenlet is not None and timeout is not None:
            greenlet.join(timeout)
            return greenlet.ready
        else:
            return True

    def kill(self):
        """Kills the running loop and waits till it gets killed."""
        assert self.has_started(), "called kill() on a non-active GeventLoop"
        self._stop_event.set()
        self._greenlet.kill()
        self._clear()

    def has_started(self):
        """
        :return: True if the loop is running
        """
        return self._greenlet is not None

    def _clear(self):
        self._greenlet = None
        self._stop_event = None


class GeventLoop(GeventLoopBase):
    """Loop class that expects an interval and a callback. A more usable scenario is to use `do_in_background`.

    For example:

    ```
    def do_some_period_maintenance():
        ...

    maintenance_job = GeventLoop(5, do_some_period_maintenance)
    maintenance_job.start()
    maintenance_job.stop()
    ```
    """
    def __init__(self, interval, callback):
        super(GeventLoop, self).__init__(interval)
        self._callback = callback

    def _loop_callback(self):
        self._callback()

    def __repr__(self):
        return "GeventLoop(interval={}, callback={!r})".format(self._interval, self._callback)


@contextmanager
def loop_in_background(interval, callback):
    """
    When entering the context, spawns a greenlet that sleeps for `interval` seconds between `callback` executions.
    When leaving the context stops the greenlet.
    The yielded object is the `GeventLoop` object so the loop can be stopped from within the context.

    For example:
    ```
    with loop_in_background(60.0, purge_cache) as purge_cache_job:
        ...
        ...
        if should_stop_cache():
            purge_cache_job.stop()
    ```
    """
    loop = GeventLoop(interval, callback)
    loop.start()
    try:
        yield loop
    finally:
        if loop.has_started():
            loop.stop()
