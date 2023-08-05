from os.path import join
import uuid
import hashlib
import random
import tempfile

from libtng import six


def get_random_socket():
    """Return a string that can be used as the address of a UNIX domain
    socket.
    """
    return join(tempfile.gettempdir(), uuid.uuid1().hex)


def get_random_long():
    """
    Get a pseudo-random long integer.

    :returns: :class:`long`
    """
    return uuid.uuid1().int >> 65


def get_random_tempdir():
    """
    Get a pseudo-random directory path.

    :returns: :class:`str`
    """
    return join(tempfile.gettempdir(), get_random_string())


def get_random_tempfile():
    """Get a random path in the operating systems' temporary directory.

    Returns:
        str
    """
    return join(tempfile.gettempdir(), get_random_string())



def get_random_string(length=32):
    """
    Get a pseudo-random string of a specified length.

    :param length: specifies the length of the output string.
    :type length: :class:`int`
    :returns: :class:`str`
    """
    value = ''
    while len(value) <= length:
        value += uuid.uuid1().hex
    return value[:length]


def get_random_phonenumber():
    return '+316' + str(random.randint(10000000, 99999999))


def get_random_email(ext='com'):
    """
    Get a random and unique e-mail address.

    :param ext: specifies the top-level domain of the output e-mail address.
    :returns: :class:`str`
    """
    return "%s@%s.%s" % (
        uuid.uuid1().hex[:16],
        uuid.uuid1().hex[:16],
        ext.strip('.')
    )


def get_random_path(n=4, sep='/'):
    """
    Get a pseudo-random filesystem path. Do **not** use for actual
    temporary directories.

    :param n: the length of each individual path component.
    :param sep: the path component separator. Default is '/'
    :returns: :class:`str`
    """
    line = uuid.uuid4().hex
    parts = [line[i:i+n] for i in range(0, len(line), n)]
    path = '/'.join(parts)
    return ('/' + path).replace('/', sep), len(parts)


def get_random_hash(algorithm='sha1', encoding=None):
    """
    Return a pseudo-random hash, optionally in a specified `encoding`.
    The `algorithm` parameter specifies the hashing algorithm, either
    a hasher from :mod:`hashlib` or a callable exposing a similar
    API.

    :param algorithm: the hash algorithm to use.
    :param encoding: the desired encoding of the output string.
    :returns: :class:`str`
    """
    h = getattr(hashlib, algorithm)() if not callable(algorithm)\
        else algorithm
    h.update(uuid.uuid1().hex)
    value = h.digest()
    if encoding:
        value = value.encode(encoding).strip()
    return value
