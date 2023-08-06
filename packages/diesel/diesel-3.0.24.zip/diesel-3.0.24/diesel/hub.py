# vim:ts=4:sw=4:expandtab
'''An event hub that supports sockets and timers, based
on Python 2.6's select & epoll support.
'''
try:
    import select26 as select
except ImportError:
    import select

try:
    import pyev
except:
    have_libev = False
else:
    have_libev = True

import errno
import fcntl
import os
import signal
import thread

from collections import deque, defaultdict
from operator import attrgetter
from time import time
from Queue import Queue, Empty

TRIGGER_COMPARE = attrgetter('trigger_time')

class ExistingSignalHandler(Exception):
    pass

class Timer(object):
    '''A timer is a promise to call some function at a future date.
    '''
    ALLOWANCE = 0.03 # If we're within 30ms, the timer is due
    def __init__(self, hub, interval, f, *args, **kw):
        self.hub = hub
        self.trigger_time = time() + interval
        self.f = f
        self.args = args
        self.kw = kw
        self.pending = True
        self.inq = False
        self.hub_data = None

    def cancel(self):
        self.pending = False
        if self.inq:
            self.inq = False
            self.hub.remove_timer(self)
            self.hub = None

    def callback(self):
        '''When the external entity checks this timer and determines
        it's due, this function is called, which calls the original
        callback.
        '''
        self.pending = False
        self.inq = False
        self.hub = None
        return self.f(*self.args, **self.kw)

    @property
    def due(self):
        '''Is it time to run this timer yet?

        The allowance provides some give-and-take so that if a
        sleep() delay comes back a little early, we still go.
        '''
        return (self.trigger_time - time()) < self.ALLOWANCE

class _PipeWrap(object):
    def __init__(self, p):
        self.p = p

    def fileno(self):
        return self.p

class IntWrap(_PipeWrap): pass

class AbstractEventHub(object):
    def __init__(self):
        self.timers = []
        self.new_timers = []
        self.run = True
        self.events = {}
        self.run_now = deque()
        self.fdmap = {}
        self.fd_ids = defaultdict(int)
        self._setup_threading()
        self.reschedule = deque()

    def _setup_threading(self):
        self._t_recv, self._t_wakeup = os.pipe()
        fcntl.fcntl(self._t_recv, fcntl.F_SETFL, os.O_NONBLOCK)
        fcntl.fcntl(self._t_wakeup, fcntl.F_SETFL, os.O_NONBLOCK)
        self.thread_comp_in = Queue()

        def handle_thread_done():
            try:
                os.read(self._t_recv, 65536)
            except IOError:
                pass
            while True:
                try:
                    c, v = self.thread_comp_in.get(False)
                except Empty:
                    break
                else:
                    c(v)
        self.register(_PipeWrap(self._t_recv), handle_thread_done, None, None)

    def remove_timer(self, t):
        try:
            self.timers.remove(t)
        except IndexError:
            pass

    def run_in_thread(self, reschedule, f, *args, **kw):
        def wrap():
            try:
                res = f(*args, **kw)
            except Exception, e:
                self.thread_comp_in.put((reschedule, e))
            else:
                self.thread_comp_in.put((reschedule, res))
            self.wake_from_other_thread()
        thread.start_new_thread(wrap, ())

    def wake_from_other_thread(self):
        try:
            os.write(self._t_wakeup, '\0')
        except IOError:
            pass

    def schedule_loop_from_other_thread(self, l, v=None):
        self.thread_comp_in.put((l.wake, v))
        self.wake_from_other_thread()

    def handle_events(self):
        '''Run one pass of event handling.
        '''
        raise NotImplementedError

    def call_later(self, interval, f, *args, **kw):
        '''Schedule a timer on the hub.
        '''
        t = Timer(self, interval, f, *args, **kw)
        self.new_timers.append(t)
        return t

    def schedule(self, c, reschedule=False):
        if reschedule:
            self.reschedule.append(c)
        else:
            self.run_now.append(c)

    def register(self, fd, read_callback, write_callback, error_callback):
        '''Register a socket fd with the hub, providing callbacks
        for read (data is ready to be recv'd) and write (buffers are
        ready for send()).

        By default, only the read behavior will be polled and the
        read callback used until enable_write is invoked.
        '''
        fn = fd.fileno()
        self.fdmap[fd] = fn
        self.fd_ids[fn] += 1
        assert fn not in self.events
        self.events[fn] = (read_callback, write_callback, error_callback)
        self._add_fd(fd)

    def add_signal_handler(self, sig, callback):
        '''Run the given callback when signal sig is triggered.'''
        raise NotImplementedError

    def _add_fd(self, fd):
        '''Add this socket to the list of sockets used in the
        poll call.
        '''
        raise NotImplementedError

    def enable_write(self, fd):
        '''Enable write polling and the write callback.
        '''
        raise NotImplementedError

    def disable_write(self, fd):
        '''Disable write polling and the write callback.
        '''
        raise NotImplementedError

    def unregister(self, fd):
        '''Remove this socket from the list of sockets the
        hub is polling on.
        '''
        if fd in self.fdmap:
            fn = self.fdmap.pop(fd)
            del self.events[fn]

            self._remove_fd(fd)

    def _remove_fd(self, fd):
        '''Remove this socket from the list of sockets the
        hub is polling on.
        '''
        raise NotImplementedError

    @property
    def describe(self):
        raise NotImplementedError()

class EPollEventHub(AbstractEventHub):
    '''A epoll-based hub.
    '''
    def __init__(self):
        self.epoll = select.epoll()
        self.signal_handlers = defaultdict(deque)
        super(EPollEventHub, self).__init__()

    @property
    def describe(self):
        return "hand-rolled select.epoll"

    def handle_events(self):
        '''Run one pass of event handling.

        epoll() is called, with a timeout equal to the next-scheduled
        timer.  When epoll returns, all fd-related events (if any) are
        handled, and timers are handled as well.
        '''
        while self.run_now and self.run:
            self.run_now.popleft()()

        if self.new_timers:
            for tr in self.new_timers:
                if tr.pending:
                    tr.inq = True
                    self.timers.append(tr)
            self.timers.sort(key=TRIGGER_COMPARE, reverse=True)
            self.new_timers = []

        tm = time()
        timeout = (self.timers[-1].trigger_time - tm) if self.timers else 1e6
        # epoll, etc, limit to 2^^31/1000 or OverflowError
        timeout = min(timeout, 1e6)
        if timeout < 0 or self.reschedule:
            timeout = 0

        # Run timers first, to try to nail their timings
        while self.timers and self.timers[-1].due:
            t = self.timers.pop()
            if t.pending:
                t.callback()
                while self.run_now and self.run:
                    self.run_now.popleft()()
                if not self.run:
                    return

        # Handle all socket I/O
        try:
            for (fd, evtype) in self.epoll.poll(timeout):
                fd_id = self.fd_ids[fd]
                if evtype & select.EPOLLIN or evtype & select.EPOLLPRI:
                    self.events[fd][0]()
                elif evtype & select.EPOLLERR or evtype & select.EPOLLHUP:
                    self.events[fd][2]()

                # The fd could have been reassigned to a new socket or removed
                # when running the callbacks immediately above. Only use it if
                # neither of those is the case.
                use_fd = fd_id == self.fd_ids[fd] and fd in self.events
                if evtype & select.EPOLLOUT and use_fd:
                    self.events[fd][1]()

                while self.run_now and self.run:
                    self.run_now.popleft()()

                if not self.run:
                    return
        except IOError, e:
            if e.errno == errno.EINTR:
                while self.run_now and self.run:
                    self.run_now.popleft()()
            else:
                raise

        self.run_now = self.reschedule
        self.reschedule = deque()

    def add_signal_handler(self, sig, callback):
        existing = signal.getsignal(sig)
        if not existing:
            signal.signal(sig, self._report_signal)
        elif existing != self._report_signal:
            raise ExistingSignalHandler(existing)
        self.signal_handlers[sig].append(callback)

    def _report_signal(self, sig, frame):
        for callback in self.signal_handlers[sig]:
            self.run_now.append(callback)
        self.signal_handlers[sig] = deque()
        signal.signal(sig, signal.SIG_DFL)

    def _add_fd(self, fd):
        '''Add this socket to the list of sockets used in the
        poll call.
        '''
        self.epoll.register(fd, select.EPOLLIN | select.EPOLLPRI)

    def enable_write(self, fd):
        '''Enable write polling and the write callback.
        '''
        self.epoll.modify(
                fd, select.EPOLLIN | select.EPOLLPRI | select.EPOLLOUT)

    def disable_write(self, fd):
        '''Disable write polling and the write callback.
        '''
        self.epoll.modify(fd, select.EPOLLIN | select.EPOLLPRI)

    def _remove_fd(self, fd):
        '''Remove this socket from the list of sockets the
        hub is polling on.
        '''
        self.epoll.unregister(fd)

class LibEvHub(AbstractEventHub):
    def __init__(self):
        self._ev_loop = pyev.default_loop()
        self._ev_watchers = {}
        self._ev_fdmap = {}
        AbstractEventHub.__init__(self)

    def add_signal_handler(self, sig, callback):
        existing = signal.getsignal(sig)
        if existing:
            raise ExistingSignalHandler(existing)
        watcher = self._ev_loop.signal(sig, self._signal_fired)
        self._ev_watchers[watcher] = callback
        watcher.start()

    @property
    def describe(self):
        return "pyev/libev (%s/%s) backend=%s" % (
                self._pyev_version() + ({
                    1  : "select()",
                    2  : "poll()",
                    4  : "epoll()",
                    8  : "kqueue()",
                    16 : "/dev/poll",
                    32 : "event ports",
                    }.get(self._ev_loop.backend, "UNKNOWN"),))

    def _pyev_version(self):
        if hasattr(pyev, 'version'):
            return pyev.version()
        else:
            pyev_ver = pyev.__version__
            libev_ver = ".".join(str(p) for p in pyev.abi_version())
            return (pyev_ver, libev_ver)

    def handle_events(self):
        '''Run one pass of event handling.
        '''
        while self.run_now and self.run:
            self.run_now.popleft()()

        if not self.run:
            self._ev_loop.stop()
            del self._ev_loop
            return

        if self.run_now or self.reschedule:
            self._ev_loop.start(pyev.EVRUN_NOWAIT)
        else:
            while not self.run_now:
                self._ev_loop.start(pyev.EVRUN_ONCE)

        while self.run_now and self.run:
            self.run_now.popleft()()

        self.run_now.extend(self.reschedule)
        self.reschedule = deque()

    def call_later(self, interval, f, *args, **kw):
        '''Schedule a timer on the hub.
        '''
        t = Timer(self, interval, f, *args, **kw)
        t.inq = True
        evt = self._ev_loop.timer(interval, 0, self._ev_timer_fired)
        t.hub_data = evt
        self._ev_watchers[evt] = t
        evt.start()
        return t

    def _ev_timer_fired(self, watcher, revents):
        t = self._ev_watchers.pop(watcher)
        if t.hub_data:
            t.hub_data = None
            self.run_now.append(t.callback)

    def remove_timer(self, t):
        evt = t.hub_data
        if evt in self._ev_watchers:
            del self._ev_watchers[evt]
            evt.stop()

    def schedule(self, c, reschedule=False):
        if reschedule:
            self.reschedule.append(c)
        else:
            self.run_now.append(c)

    def _signal_fired(self, watcher, revents):
        callback = self._ev_watchers.pop(watcher)
        watcher.stop()
        self.run_now.append(callback)

    def _ev_io_fired(self, watcher, revents):
        r, w, e = self.events[watcher.fd]
        if revents & pyev.EV_READ:
            self.run_now.append(r)
        if revents & pyev.EV_WRITE:
            self.run_now.append(w)
        if revents & pyev.EV_ERROR:
            self.run_now.append(e)

    def _add_fd(self, fd):
        '''Add this socket to the list of sockets used in the
        poll call.
        '''
        assert fd not in self._ev_fdmap
        rev = self._ev_loop.io(fd, pyev.EV_READ, self._ev_io_fired)
        wev = self._ev_loop.io(fd, pyev.EV_WRITE, self._ev_io_fired)
        self._ev_fdmap[fd] = rev, wev
        rev.start()

    def enable_write(self, fd):
        '''Enable write polling and the write callback.
        '''
        self._ev_fdmap[fd][1].start()

    def disable_write(self, fd):
        '''Disable write polling and the write callback.
        '''
        self._ev_fdmap[fd][1].stop()

    def _remove_fd(self, fd):
        '''Remove this socket from the list of sockets the
        hub is polling on.
        '''
        rev, wev = self._ev_fdmap.pop(fd)
        rev.stop()
        wev.stop()

# Expose a usable EventHub implementation
if (os.environ.get('DIESEL_LIBEV') or
    os.environ.get('DIESEL_NO_EPOLL') or
    not hasattr(select, 'epoll')):
    assert have_libev, "if you don't have select.epoll (not on linux?), please install pyev!"
    EventHub = LibEvHub
else:
    EventHub = EPollEventHub
