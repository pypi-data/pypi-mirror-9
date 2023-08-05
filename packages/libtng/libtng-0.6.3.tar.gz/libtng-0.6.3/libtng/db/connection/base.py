from importlib import import_module
import copy

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import ArgumentError

from libtng import const
from libtng.functional import SimpleLazyObject, cached_property
from libtng.db.connection.exceptions import ConnectionAlreadyExists
from libtng.db.connection.exceptions import ConnectionDoesNotExist
from libtng.exceptions import InvalidDataSourceName


class ConnectionOptions(object):
    """
    A :class:`ConnectionOptions` instance specifies the parameters
    needed to connect to a database system.
    """

    @cached_property
    def handler(self):
        return self.get_handler()

    @property
    def dsn(self):
        return self.handler.dsn

    def format_dsn(self, dsn_tpl):
        return dsn_tpl.format(**self.__params)

    @property
    def backend(self):
        return self.__backend

    @property
    def engine(self):
        return self.__engine

    def __init__(self, alias, backend, **params):
        """
        Initializes a new :class:`ConnectionOptions` instance.

        :param alias:
            a string specfying the alias for the connection.
        :param backend:
            a string specifying the module import path to a database
            system backend. Valid backends are:
            -   ``libtng.db.backends.postgresql_psycopg2``
        :param params:
            keyword arguments specifying the connection parameters.
        """
        self.__engine = backend
        self.__params = params
        self.__backend = SimpleLazyObject(lambda: self.handler)

    def get_handler(self):
        """
        Return the :attr:`ConnectionOptions.backend` handler.
        """
        handler = import_module(self.engine).ConnectionHandler(self)
        return handler

    @property
    def NAME(self):
        return self.__params['database']

    @property
    def USER(self):
        return self.__params['user']

    @property
    def PASSWORD(self):
        return self.__params['password']

    @property
    def HOST(self):
        return self.__params['host']

    @property
    def PORT(self):
        return self.__params.get('port') or self.backend.default_port

    @property
    def ENGINE(self):
        return self.__engine

    @property
    def APPLICATION_NAME(self):
        return self.__params.get('application_name') \
            or self.backend.application_name

    @property
    def APPLICATION_VERSION(self):
        return self.__params.get('application_version') \
            or self.backend.application_version


class ConnectionManager(object):
    """
    :class:`ConnectionManager` objects create and manage connections
    to database servers.
    """
    _databases = {}
    _options = {}
    _sessionmakers = {}

    def add(self, alias, dsn, echo=False, **options):
        """Add a new connection to the connection manager.

        Args:
            alias: a string specifying the connection alias.
            dsn: a string containing the DSN used to connect.

        Kwargs:
            echo: a boolean indicating if debug messages should be
                printed to stdout for this connection.
            **options: connection options.

        Returns:
            None
        """
        if alias in self._databases:
            raise ConnectionAlreadyExists(
                "Connection with alias '{0}' already exists.".format(alias))
        try:
            self._databases[alias] = create_engine(dsn, echo=echo, **options)
        except ArgumentError: # Invalid DSN
            raise InvalidDataSourceName(dsn)
        self._sessionmakers[alias] = scoped_session(
            sessionmaker(
                bind=self._databases[alias],
                expire_on_commit = False,
                #class_ = cls,
                autocommit = True,
                autoflush=False
            )
        )

    def get_options(self, alias):
        """
        Return a :class:`ConnectionOptions` instance representing
        the configuration for the database connection identified
        by `alias`.
        """
        try:
            return self._options[alias]
        except KeyError:
            raise ConnectionDoesNotExist("Connection '{0}' is not specified."\
                .format(alias))

    def destroy(self, alias, recreate=True):
        """
        Closes all connections to the database identified by `alias`. The
        caller should ensure that there are no ongoing transactions.

        :param alias:
            a string identifying the database.
        :param recreate:
            a boolean indicating if the connection should be recreated.
            Default is ``True``.
        """
        engine = self._databases.pop(alias, None)
        if engine is not None:
            engine.dispose()
        if recreate:
            self._databases[alias] = self.get_connection(alias)

    def set_options(self, alias, engine, params, reconnect=False):
        """
        Sets options for the given `alias`.

        :param alias:
            identifies the database connection.
        :param engine:
            specifies the database engine.
        """
        self._options[alias] = ConnectionOptions(alias, engine, **params)
        if reconnect:
            self.destroy(alias, recreate=True)

    def load_options(self, databases, reconnect=True):
        """
        Loads options for the specified `databases`.

        :param databases:
            a :class:`dict` specifying database connections.
            Must conform to the format used by :mod:`django`.
        :param reconnect:
            indicates if all connections should be updated immediatly;
            effectively closing and recreating them.
        """
        for alias, params in databases.items():
            self.set_options(alias, params['engine'], params,
                reconnect=reconnect)

    def get_session(self, alias, scoped=True, echo=True, *args, **kwargs):
        return self._sessionmakers[alias](*args, **kwargs)

    def get_connection(self, alias):
        """
        Return a new database connection.
        :param alias:
            a string specifying the database alias.

        :returns:
            a :class:`sqlalchemy.engine.base.Connection` instance.
        """
        if alias in self._databases:
            raise Exception("Already connected.")
        self._connect(alias)
        return self._databases[alias]

    def _connect(self, alias):
        self._databases[alias] = create_engine(self.get_options(alias).dsn, echo=True)
        self._databases[alias].echo = True
        self._sessionmakers[alias] = scoped_session(
            sessionmaker(
                bind=self._databases[alias],
                expire_on_commit = False,
                echo=True,
                #class_ = cls,
                autocommit = True,
                autoflush=False
            )
        )

    def __getitem__(self, alias):
        if alias not in self._options:
            raise ConnectionDoesNotExist("Connection '{0}' is not specified."\
                .format(alias))
        if alias not in self._databases:
            self._connect(alias)
        return self._databases[alias]


connections = ConnectionManager()
default_connection = SimpleLazyObject(lambda: connections[const.DEFAULT_DB_ALIAS])


del ConnectionManager
