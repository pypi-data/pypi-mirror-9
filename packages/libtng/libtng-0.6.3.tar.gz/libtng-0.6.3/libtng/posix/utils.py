import os
import stat
import errno
import shlex
import subprocess

from libtng import six

__all__ = [
    'get_bin_path',
    'is_executable',
    'run_command'
]


def get_bin_path(executable_name, opt_dirs=None, fail_silent=False):
    """
    Find a system executable by inspecting the PATH environment
    variable.

    :param executable_name:
        the name of the executable.
    :type executable_name:
        :class:`str`
    :param opt_dirs:
        a list of directories to search for in addition to PATH.
    :param fail_silent:
        indicates that :func:`get_bin_path()` should fail silently
        if no binary was found, returning ``None`` instead.
    :returns: :class:`str`
    :raises: :exc:`IOError`
    """
    opt_dirs = opt_dirs or []
    sbin_paths = ['/sbin', '/usr/sbin', '/usr/local/sbin']
    paths = []
    for d in opt_dirs:
        if d is not None and os.path.exists(d):
            paths.append(d)
    paths += os.environ.get('PATH', '').split(os.pathsep)
    bin_path = None
    # mangle PATH to include /sbin dirs
    for p in sbin_paths:
        if p not in paths and os.path.exists(p):
            paths.append(p)
    for d in paths:
        path = os.path.join(d, executable_name)
        if os.path.exists(path) and is_executable(path):
            bin_path = path
            break
    if bin_path is None and not fail_silent:
        msg = 'Failed to find required executable {0}'.format(executable_name)
        raise IOError(errno.ENOENT, msg)
    return bin_path


def is_executable(path):
    """
    Check if given `path` is executable.

    :param path:
        a path on the local filesystem.
    :returns: :class:`bool`
    """
    return (stat.S_IXUSR & os.stat(path)[stat.ST_MODE]
        or stat.S_IXGRP & os.stat(path)[stat.ST_MODE]
        or stat.S_IXOTH & os.stat(path)[stat.ST_MODE])


def run_command(args, close_fds=False, executable=None, data=None,
    binary_data=False, path_prefix=None, cwd=None, use_unsafe_shell=False,
    fail_silent=True):
    """
    Execute a command, returns `returncode`, `stdout`, and `stderr`.

    :param args:
        Commands to run. When `args` is a list, the command will
        be run with ``shell=False``. If args is a string and
        ``use_unsafe_shell=False`` it will split args to a list
        and run with ``shell=False``. If args is a string and
        ``use_unsafe_shell=True`` it run with ``shell=True``.
    :param use_unsafe_shell:
        Indicates if a shell may be used when `args` is a
        :class:`str`.
    :param close_fds:
        See documentation for :class:`subprocess.Popen()`. Default is
        ``False``.
    :param executable:
        See documentation for :class:`subprocess.Popen()`. Default is
        ``False``.
    :type executable:
        :class:`str`
    :param cwd:
        Optionally specify the working directory wherein the command
        is run.
    :param data:
        Data to pass to the commands' `stdin`.
    :param fail_silent:
        fail silent on nonzero returncode.
    :returns:
        :class:`tuple`
    """
    shell = False
    if isinstance(args, list):
        pass
    elif isinstance(args, basestring) and use_unsafe_shell:
        shell = True
    elif isinstance(args, basestring):
        args = shlex.split(args)
    else:
        msg = "Argument `args` to run_command must be list or string"
        raise ValueError(msg)

    # expand things like $HOME and ~
    if not shell:
        args = [ os.path.expandvars(os.path.expanduser(x)) for x in args ]
    rc = 0
    msg = None
    st_in = None

    # Set a temporart env path if a prefix is passed
    env=os.environ
    if path_prefix:
        env['PATH']="%s:%s" % (path_prefix, env['PATH'])
    if data:
        st_in = subprocess.PIPE
    kwargs = dict(
        executable=executable,
        shell=shell,
        close_fds=close_fds,
        stdin= st_in,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    if path_prefix:
        kwargs['env'] = env
    if cwd and os.path.isdir(cwd):
        kwargs['cwd'] = cwd


    # make sure we're in the right working directory and proceed
    # to run the command.
    if cwd and os.path.isdir(cwd):
        os.chdir(cwd)
    cmd = subprocess.Popen(args, **kwargs)
    if data:
        if not binary_data:
            data += '\n'
    out, err = cmd.communicate(input=data)
    rc = cmd.returncode
    if (rc != 0) and not fail_silent:
        msg = "{0} exited with nonzero returncode ({1}). Output from stderr was: {2}"\
            .format(' '.format(args), rc, err.rstrip())
        raise RuntimeError(msg)
    return (rc, out, err)