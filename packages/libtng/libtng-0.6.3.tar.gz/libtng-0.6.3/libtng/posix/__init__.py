"""
Utility functions for systems running operating systems conforming
to the Portable Operating-System Interface (POSIX) specification.
"""
"""
:mod:`os` from the standard library with additional features.
"""
from utils import *
import user


__all__ = [
    'get_bin_path',
    'is_executable',
    'run_command',
    'chown'
]



def chown(dirname, user, recursive=False, group=None, preserve_root=False, from_owner=None, from_group=None, rfile=None):
    """
    Change the owner and/or group of each FILE to OWNER and/or GROUP.
    With `rfile`, change the owner and group of each FILE to
    those of `rfile`.

    :param recursive:
        operate on files and directories recursively.
    :param group:
        specifies the group.
    :param preserve_root:
        fail to operate recursively on `/'.
    :param from_owner:
        change the owner and/or group of each file only if
        its current owner and/or group match those specified
        here.  Either may be omitted, in which case a match
        is not required for the omitted attribute.
    :param from_group:
        see `from_owner`.
    :param rfile:
        use `rfile`'s owner and group rather than
        specifying OWNER:GROUP values.
    """
    args = [get_bin_path('chown')]
    if recursive:
        args.append('-R')
    if preserve_root:
        args.append('--preserve-root')
    if from_owner:
        from_group = from_group or from_owner
        args.extend(['--from', '{0}:{1}'.format(from_owner, from_group)])
    if rfile:
        args.extend(['--reference', rfile])
    else:
        args.extend(['{0}:{1}'.format(user, group or user), dirname])
    run_command(args)