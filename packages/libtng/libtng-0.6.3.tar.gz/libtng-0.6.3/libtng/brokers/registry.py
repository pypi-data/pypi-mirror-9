from libtng.brokers.broker import Broker


class BrokerRegistry(object):

    def __init__(self):
        self._registry = {}

    def add(self, alias, dsn):
        """
        Adds a new :class:`Broker` to the registry.

        Args:
            alias (str): an alias to reference the broker by.
            dsn (dsn): the DSN used to connect to the broker.

        Returns:
            None
        """
        self._registry[alias] = Broker(alias, dsn)

    def task(self, alias):
        """
        Decorates a function for use in asynchronous task processing
        with Celery.

        Args:
            alias (str): identifier the broker connection.

        Returns:
            types.MethodType
        """
        return self._registry[alias].task()

    def get(self, alias):
        """
        Returns a registered :class:`Broker` instance.
        """
        return self._registry[alias]

    def init_celery(self, alias, app_class, *args, **kwargs):
        """
        Initializes a new :class:`celery.Celery` instance using the
        specified broker.

        Args:
            alias (str): identifies the broker.
            app_class: a callable that produces a :class:`celery.Celery`
                instance.

        Returns:
            None
        """
        return self._registry[alias].init_celery(app_class, *args, **kwargs)


brokers = BrokerRegistry()