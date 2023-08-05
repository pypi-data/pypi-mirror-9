"""
Various algorithms to calculate a checksum and/or control digit
for an arbitrary value.
"""
from libtng.checksum.algorithms import Verhoeff
from libtng.checksum.checksum import Checksum


def checksum(algorithm, value):
    """
    Calculate a checksum for the specified value.
    """
    c = algorithm()
    return c.checksum(value)


def get(algorithm, value):
    """
    Process `value` so that it passes `algorithm`.
    """
    a = algorithm()
    return a.get(value)


def is_valid(algorithm_type, value):
    """
    Return a :class:`bool` indicating if `value` passes the
    specified `algorithm_type`.

    Args:
        algorithm_type (libtng.checksum.Checksum): a conret~e
            checksum algorithm implementation.

    Returns:
        bool
    """
    algorithm = algorithm_type()
    return algorithm.is_valid(value)