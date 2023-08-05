import os
import select
import sys
import multiprocessing
import signal
import time


class Daemon(object):
    """Creates a well-behaved UNIX daemon."""

    def __init__(self, pidfile, target=None, *args, **kwargs):
        self.pidfile = pidfile
        self.target = target
        self.stdin = kwargs.pop('stdin', '/dev/null')
        self.stdout = kwargs.pop('stdout', '/dev/null')
        self.stderr = kwargs.pop('stderr', '/dev/null')
        self._on_sighup = kwargs.pop('on_sighup', lambda s, f: None)
        self._on_sigint = kwargs.pop('on_sigint', lambda s, f: None)
        self._on_sigterm = kwargs.pop('on_sigterm', lambda s, f: None)
        self.pid = None
        self.readfd, self.writefd = os.pipe()
        self.parent = os.getpid()
        self.args = args
        self.kwargs = kwargs

    def start(self, block=False):
        """Starts the daemons activity; arranges for the `target`
        callable to be run in a separate process.
        
        Args:
            block (bool): indicates if `meth:Daemon.start()` should block until
                the daemon process is created.

        Returns:
            None
        """
        p = multiprocessing.Process(target=self.run)
        p.start()
        while not os.path.exists(self.pidfile) and block:
            time.sleep(0.01)

    def daemonize(self):
        """Double-fork the process to create a well-behaved daemon."""
        try:
            pid = os.fork()
            if pid != 0:
                sys.exit(0)
        except OSError as e:
            print("Unable to fork process (id: {0})".format(os.getpid()))
            sys.exit(1)

        # Decouple the daemon from it's parent environment.
        os.chdir('/')
        os.setsid()
        os.umask(0)

        # Proceed to the second fork.
        try:
            pid = os.fork()
            if pid != 0:
                sys.exit(0)
        except OSError as e:
            print("Unable to fork process (id: {0})".format(os.getpid()))
            sys.exit(1)

    def terminate(self, timeout=None):
        """Terminates the daemons' activity. Return a boolean indicating
        if the daemon was succesfully terminated.
        
        Args:
            timeout (float): specifies the timeout.

        Returns:
            boolean
        """
        cooldown = 0.01
        result = False
        while ((timeout > 0.0) if timeout else True):
            try:
                os.kill(self._read_pidfile(), signal.SIGTERM)
                time.sleep(cooldown)
                if timeout:
                    timeout -= cooldown
                continue
            except OSError as e:
                result = True
                break
        return result

    def run(self):
        self.daemonize()

        # Write the pidfile
        with open(self.pidfile, 'w') as f:
            f.write(str(os.getpid()))

        # Register signal handlers. Since SIGTERM and SIGINT are supposed to
        # exit a process, the pidfile will be deleted.
        signal.signal(signal.SIGTERM, self.on_sigterm)
        signal.signal(signal.SIGINT, self.on_sigint)
        signal.signal(signal.SIGHUP, self.on_sighup)

        # Redirect stdin, stdout and stderr file descriptors.
        sys.stdin = open('/dev/null', 'r')
        sys.stdout = open('/dev/null', 'w')
        sys.stderr = open('/dev/null', 'w')

        self.target(*self.args, **self.kwargs)

    def _read_pidfile(self):
        with open(self.pidfile, 'r') as f:
            return int(f.read())

    # Signal handlers
    def on_sighup(self, signum, frame):
        try:
            self._on_sighup(signum, frame)
        except Exception as e:
            print("Caught exception in SIGHUP handler: ", e, file=sys.stderr)

    def on_sigint(self, signum, frame):
        try:
            os.unlink(self.pidfile)
            self._on_sigint(signum, frame)
        except Exception as e:
            print("Caught exception in SIGINT handler: ", e, file=sys.stderr)
        sys.exit(signum)

    def on_sigterm(self, signum, frame):
        try:
            os.unlink(self.pidfile)
            self._on_sigterm(signum, frame)
        except Exception as e:
            print("Caught exception in SIGTERM handler: ", e, file=sys.stderr)
        sys.exit(signum)

