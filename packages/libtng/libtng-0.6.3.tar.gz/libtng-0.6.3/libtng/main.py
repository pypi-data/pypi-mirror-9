import atexit
import errno
import grp
import logging
import multiprocessing
import os
import pwd
import signal
import sys
import threading


class MainEventLoop(object):
    """Represents the main event loop of a long-running task. Typically used
    for server or business processes.
    """
    non_fatal_errno = (errno.EINTR, errno.EAGAIN)
    logger_name     = __module__
    logger          = property(lambda self: self.__logger)

    def __init__(self, *args, **kwargs):
        self.__must_reload = False
        self.__must_exit = False

        self.configure(*args, **kwargs)

    def as_thread(self, daemon=False):
        """Return a :class:`threading.Thread` instance configured to run
        the main event loop in a separate thread of control.
        """
        thread = threading.Thread(target=self.main_event_loop)
        if daemon:
            thread.daemon = True
        return thread

    def as_process(self):
        """Return a :class:`multiprocessing.Process` instance configured to
        run the main event loop in a separate process.
        """
        return multiprocessing.Process(target=self.main_event_loop)

    def as_daemon(self, pidfile, workdir=None, umask=0o22):
        """Daemonize the process and run the main event loop. Return a
        boolean indicating if the current process must exit.

        Args:
            pidfile (str): specifies the location of the pidfile used by the
                daemon process.
            workdir (str): the working directory of the daemon.
            umask (int): the file creation mode of the daemon process.

        Returns:
            bool
        """
        try:
            pid = os.fork()
            if pid > 0:
                return False
        except OSError as e:
            print("Fork #1 failed", file=sys.stderr)
            sys.exit(1)

        # Detach from the invoking process: set the file creation mode,
        # create a new session and change the working directory.
        os.chdir(workdir or os.getcwd())
        os.setsid()
        os.umask(umask)

        # Process to the second fork.
        try:
            pid = os.fork()
            if pid > 0:
                return False
        except OSError as e:
            print("Fork #2 failed", file=sys.stderr)
            sys.exit(1)

        # Flush and redirect the file descriptors of stdin, stdout and stderr.
        sys.stdout.flush()
        sys.stderr.flush()
        si = open(os.devnull, 'r')
        so = open(os.devnull, 'a+')
        se = open(os.devnull, 'a+')
        os.dup2(si.fileno(), sys.stdin.fileno())
        os.dup2(so.fileno(), sys.stdout.fileno())
        os.dup2(se.fileno(), sys.stderr.fileno())


        if pidfile and False:
            atexit.register(lambda: os.unlink(pidfile))
            with open(pidfile, 'w') as f:
                f.write(str(os.getpid()))
            os.wait(pid)

        self.start()

    def configure(self, *args, **kwargs):
        """Configures the main event loop so that :meth:`MainEventLoop.start()`
        can be called succesfully. This method SHOULD NOT consume any
        resources or open connections to remote services.
        """
        pass

    def _setup(self, is_reload=False):
        self.__logger = logging.getLogger(self.logger_name)
        
        # We bind the signal handlers here so we are sure they are
        # always bound in the process that executes the main event
        # loop.
        signal.signal(signal.SIGHUP, self.on_sighup)
        signal.signal(signal.SIGINT, self.on_sigint)
        signal.signal(signal.SIGTERM, self.on_sigterm)

        self.setup(is_reload=is_reload)

    def setup(self, is_reload=False):
        """Sets up the environment for the main event loop. The `is_reload`
        argument indicates if :meth:`MainEventLoop.setup` is called as the
        result of a reload (e.g. after SIGHUP).
        """
        pass

    def main_event_loop(self):
        try:
            self._setup(is_reload=False)
        except Exception as e:
            self._do_exit(is_running=False)
            raise
        self.group = grp.getgrgid(os.getgid())
        self.user = pwd.getpwuid(os.getuid())
        self.logger.info("Process running as {user}:{group}".format(
            user = self.user.pw_name,
            group = self.group.gr_name
        ))
        self.logger.info("Entering main event loop")
        self.logger.info
        while True:
            try:
                if self.must_exit():
                    self._do_exit(is_running=True)
                    break
                if self.must_reload():
                    self._do_reload()
                self.main_event()
            except NotImplementedError as e:
                raise
            except Exception as e:
                self.on_exception(e)
                if getattr(e, 'errno', None) in self.non_fatal_errno:
                    continue
                self.logger.exception(
                    "Uncaught {0} in main event loop".format(type(e).__name__))
                continue
        self.on_terminate()
        self.logger.info("Exiting main event loop")

    def main_event(self):
        raise NotImplementedError("Subclasses must override this method.")

    def on_sighup(self, signum, frame):
        self.logger.info("Caught SIGHUP, reloading runtime configuration")
        self.reload()

    def on_sigterm(self, signum, frame):
        self.stop()

    def on_sigint(self, signum, frame):
        self.logger.info("Caught SIGINT, proceeding to exit main event loop")
        self.stop()

    def reload(self):
        """Informs the main event loop that a reload is required and
        :meth:`MainEventLoop.do_reload` should be invoked.
        """
        self.__must_reload = True

    def must_reload(self):
        """Indicates if the main event loop should reload the runtime
        configuration.
        """
        return self.__must_reload

    def do_reload(self):
        """Hook that is called when the process has received a ``SIGHUP``."""
        pass

    def _do_reload(self):
        try:
            self.logger.info("Reloading runtime configuration")
            self.setup(is_reload=True)
            self.do_reload()
        except Exception as e:
            self.logger.exception(
                "Caught {0} while reloading configuration"\
                    .format(type(e).__name__)
            )
        finally:
            self.__must_reload = False
            self.logger.info("Finished reloading runtime configuration")

    def start(self):
        """Starts the main event loop."""
        self.main_event_loop()

    def stop(self):
        """Informs the main event loop that it should terminate."""
        self.__must_exit = True

    def must_exit(self):
        """Indicates if the main event loop should exit."""
        return self.__must_exit

    def do_exit(self, is_running=False):
        """Hook that allows the cleanup of resources and other tasks to
        perform when exiting the main event loop.
        """
        pass

    def _do_exit(self, is_running=False):
        try:
            self.logger.info("Tearing down main event loop")
            self.do_exit(is_running=False)
        except Exception as e:
            self.logger.exception("Caught {0} while running exit handler"\
                .format(type(e).__name__))
        finally:
            self.logger.info("Finished running exit procedures")

    def on_terminate(self):
        """Hook that is called just prior to returning from the main event
        loop.
        """
        pass

    def on_exception(self, exception):
        """Hook that is called when an exception occurred during the main event
        loop.
        """
        pass
