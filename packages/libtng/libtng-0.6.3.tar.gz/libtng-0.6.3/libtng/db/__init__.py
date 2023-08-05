"""The relational database API used by the TNG Enterprise Management
System.
"""
from libtng.db.connection import connections as _connections
from libtng.db.relation import relation_factory
from libtng.db.relation import Relation


def get_session(alias):
    """Returns a database session for a connection identified by
    the given `alias`.
    """
    return _connections.get_session(alias)


def add_connection(alias, dsn, *args, **kwargs):
    """Register a new connection `dsn` under `alias`."""
    _connections.add(alias, dsn, *args, **kwargs)
