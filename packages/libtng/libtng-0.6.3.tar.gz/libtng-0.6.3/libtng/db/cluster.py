from libtng.ddd import Provisionable


class DatabaseCluster(Provisionable):
    """
    Represents a database cluster.
    """

    def __init__(self, host, port, engine):
        self._host = host
        self._port = port
        self._engine = engine