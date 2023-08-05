"""
Manages the runtime environment for :mod:`libtng`. Use
:func:`setenv` to set an environment variable,
and :func:`getenv` to get an environment variable.

Environment variables
---------------------

.. data:: DEFAULT_DB_ALIAS

    Specifies the default database connection.


.. data:: DEFAULT_LANGUAGE

    A :class:`str` holding a language code, specifying the
    default language used in localization contexts.
"""
from libtng import const


DEFAULTS = {
    'DEFAULT_DB_ALIAS': const.DEFAULT_DB_ALIAS,
    'DEFAULT_LANGUAGE': const.DEFAULT_LANGUAGE
}


# TODO: This should be thread-local
ENVIRONMENT = {}


def setenv(key, value):
    ENVIRONMENT[key] = value


def getenv(key, default=None):
    return ENVIRONMENT.get(key, default) or DEFAULTS[key]


class Environment(object):
    pass


env = Environment()