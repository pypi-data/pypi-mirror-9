"""
Exposes a base class for long running processes.
"""
from __future__ import print_function
import atexit
import contextlib
import grp
import multiprocessing
import os
import pwd
import signal
import sys
import threading
import time
import warnings

from libtng.encoding import force_bytes


def require_privileged(error_message):
    """Requires a process to be run as a privileged user."""
    if os.getuid() != 0:
        print(error_message, file=sys.stderr)
        sys.exit(1)


@contextlib.contextmanager
def pidfile(filepath, daemon):
    """Create a pidfile for a process."""
    if not daemon:
        yield
    else:
        filepath = force_bytes(filepath)
        try:
            if os.path.exists(filepath):
                print("Pidfile present:", filepath,
                    file=sys.stderr)
                sys.exit(-1)
            with open(filepath, 'wb') as f:
                f.write(force_bytes(os.getpid()) + force_bytes('\n'))
            yield
            try:
                os.unlink(filepath)
            except (IOError, OSError):
                pass
        except IOError:
            print("Unable to write pidfile to {0}".format(filepath),
                file=sys.stderr)
            sys.exit(-1)


def drop_privileges(user, group=None):
    """Drops privileges to the specified user and group.

    Args:
        user (str): specifies the user.
        group (str): specifies the group; if `group` is 
            ``None``, it is considered the same as 
            `user`.

    Returns:
        None
    """
    group = grp.getgrnam(group or user)
    user = pwd.getpwnam(user)
    os.setgid(group.gr_gid)
    os.setuid(user.pw_uid)



class BaseProcess(object):
    default_signals = [
        signal.SIGTERM,
        signal.SIGHUP,
        signal.SIGINT
    ]
    signals = []

    @classmethod
    def as_process(cls, defer=True, args=None, kwargs=None):
        args, kwargs = args or [], kwargs or {}
        p = cls(*args, **kwargs)
        return p.start_process(defer=defer)

    @classmethod
    def as_thread(cls, daemon=False, defer=True, args=None, kwargs=None):
        args, kwargs = args or [], kwargs or {}
        p = cls(*args, **kwargs)
        return p.start_threaded(daemon=daemon, defer=defer)

    def __init__(self, setupfunc=None, suppress_exceptions=False, framerate=None):
        """Initialize a new :class:`BaseProcess` instance.

        Args:
            setupfunc: a callable responsible for setting up the environment
                before entering the main event loop.
            suppress_exceptions (bool): indicates if exceptions are to be
                suppressed. Default is False, meaning that exceptions will
                be raised after cleaning up.
            framerate: specifies a waiting period after finished one
                event loop.
        """
        self._needs_update = True
        self._must_exit = False
        self._setupfunc = setupfunc
        self._suppress_exceptions = suppress_exceptions
        self._framerate = framerate
        self.signals = tuple(
            set(list(self.signals) + list(self.default_signals)))
        
        # The execution time of the last event loop.
        self.previous_execution_time = 1 

    def setup(self):
        """Hook to set up the process state."""
        pass

    def register_signals(self):
        """Binds signals to the :meth:`BaseProcess.signal_handler`
        method.
        """
        pass

    def run(self):
        warnings.warn("run() is deprecated, use start() instead",
            DeprecationWarning, stacklevel=2)
        self.start()

    def start_threaded(self, defer=False, daemon=False):
        """Arrange for the main event loop to be started in a separate
        thread of control.

        Args:
            defer (bool): defer starting the main event loop.
            daemon (bool): indicates that the thread is a daemon,
                causing it to terminate when it's parent thread
                has terminated.

        Returns:
            threading.Thread
        """
        thread = threading.Thread(target=self.start)
        if daemon:
            thread.daemon = True
        if not defer:
            thread.start()
        return thread

    def start_process(self, defer=False):
        """Arrange for the main event loop to be started in a separate
        process.

        Args:
            defer (boolean): defer starting the main event loop.

        Returns:
            multiprocessing.Process
        """
        process = multiprocessing.Process(target=self.start)
        if not defer:
            process.start()
        return process

    def start(self):
        """Enter the process main loop and execute the
        :func:`BaseProcess.main_event_loop`.
        """
        logger = getattr(self, '_logger', None)

        # Setup the process.
        self.setup()

        # If a setup callable has been passed to the process
        # constructor.
        if self._setupfunc is not None:
            self._setupfunc(self)

        # Bind signals here. To change this behavior, override
        # register_signals().
        self.register_signals()

        exception = None
        while True:
            started = time.time()
            try:
                # Check if we need to exit and if so bail out
                # immediately.
                if self.must_exit():
                    if logger:
                        logger.debug("Cleaning up and existing.")
                    self.do_cleanup(True)
                    self.do_exit()
                    break

                # if the update() method has been called,
                # refresh the state of the process.
                if self._needs_update:
                    self._do_update()

                try:
                    started = time.time()
                    self.main_event()
                    ended = time.time()
                    self.previous_execution_time = ended - started
                except NotImplementedError:
                    raise
                except Exception as exception:
                    if self.exception_handler(exception):
                        self.do_cleanup(False)
                        if self._must_exit: # Don't raise if we must exit.
                            return
                        raise
                
            except KeyboardInterrupt:
                self.join()

    def main_event(self):
        raise NotImplementedError

    def must_exit(self):
        """Returns a boolean indicating if the main event loop
        should exit.
        """
        return self._must_exit is True

    def update(self):
        """Indicates that :meth:`BaseProcess.do_update`
        should be called."""
        self._needs_update = True

    def join(self):
        """Gracefully exits the process."""
        self._must_exit = True

    def exit(self):
        """Gracefully exits the process."""
        self._must_exit = True

    def stop(self):
        """Gracefully exits the process."""
        self._must_exit = True

    def terminate(self):
        """Exits the process."""
        self._must_exit = True

    def _do_update(self):
        try:
            self.do_update()
        finally:
            self._needs_update = False

    def do_update(self):
        """Hook to update the program state."""
        pass

    def do_exit(self):
        """Gracefully exit the process. May perform any cleanup
        tasks needed by the process."""
        pass

    def do_cleanup(self, gracecul):
        """Performs cleanup prior to exiting (wether it's gracecul or
        caused by an exception).

        Args:
            graceful: indicates if the cleanup is the result of a
                graceful main event loop interruption.

        Returns:
            None
        """
        pass

    def signal_handler(self, signum, frame):
        if signum == signal.SIGHUP:
            self.update()
        if signum in (signal.SIGTERM, signal.SIGINT):
            self.do_cleanup(signum == signal.SIGINT)
            self._must_exit = True
            self.do_exit()

    def exception_handler(self, exception):
        """Hook to handle a fatal exception in the main event loop.
        MUST return a boolean indicating if the exception should
        be reraised.
        """
        return True

    def teardown(self):
        """Releases all resources and locks claimed by the process."""


