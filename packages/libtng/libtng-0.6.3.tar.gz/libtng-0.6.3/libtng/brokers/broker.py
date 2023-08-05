


class Broker(object):

    def __init__(self, alias, dsn):
        self._alias = alias
        self._dsn = dsn
        self._app = None

    def task(self):
        """
        Decorates a function for use in asynchronous task processing
        with Celery.
        """
        if self._app is None:
            raise RuntimeError("Celery application not configured. Call init_celery() before proceeding.")
        return self._app.task


    def init_celery(self, app_class, module_name, backend_url=None):
        """
        Return a new :class:`celery.Celery` instance.

        Args:
            app_class: the factory returning a new :class:`celery.Celery`
                instance.

        Returns:
            celery.Celery
        """
        self._app = app_class(module_name, backend=backend_url or self._dsn, broker=self._dsn)
        return self._app