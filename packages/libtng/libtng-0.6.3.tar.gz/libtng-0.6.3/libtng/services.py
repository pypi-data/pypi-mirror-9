"""
Specifies mixins for service-dependencies.
"""
from importlib import import_module


class HTTPDependantMixin(object):
    """
    Mixin class for services depending on HTTP requests. The constructor
    must set a `_request_factory` attribute, holding a Python object exposing
    methods for each HTTP verb (e.g. ``get``, ``put``, ``post``, ..).
    """

    def _http_request(self, method, *args, **kwargs):
        f = getattr(self._request_factory, method)
        return f(*args, **kwargs)

    def _http_get(self, *args, **kwargs):
        return self._http_request('get', *args, **kwargs)

    def _http_post(self, *args, **kwargs):
        return self._http_request('post', *args, **kwargs)

    def _http_options(self, *args, **kwargs):
        return self._http_request('options', *args, **kwargs)

    def _http_delete(self, *args, **kwargs):
        return self._http_request('delete', *args, **kwargs)

    def _http_put(self, *args, **kwargs):
        return self._http_request('put', *args, **kwargs)

    def _http_patch(self, *args, **kwargs):
        return self._http_request('patch', *args, **kwargs)


import logging


class LoggerMixin(object):
    """Mixin class for services that use a logger. The constructor
    must set a `_logger` attribute."""

    def _log(self, level, message, *args, **kwargs):
        if self._logger is not None:
            self._logger.log(level, message, *args, **kwargs)

    def _log_debug(self, message, *args, **kwargs):
        return self._log(logging.DEBUG, message, *args, **kwargs)

    def _log_info(self, message, *args, **kwargs):
        return self._log(logging.INFO, message, *args, **kwargs)

    def _log_error(self, message, *args, **kwargs):
        return self._log(logging.ERROR, message, *args, **kwargs)

    def _log_critical(self, message, *args, **kwargs):
        return self._log(logging.CRITICAL, message, *args, **kwargs)

    def _log_warning(self, message, *args, **kwargs):
        return self._log(logging.WARNING, message, *args, **kwargs)


class DatabaseMixin(object):
    """Mixin class for services that make use of a database connection.
    The constructor must set a ``_session`` attribute."""

    _query_class = None

    @property
    def query_class(self):
        if self._query_class is None:
            self._query_class = import_module('sqlalchemy.orm').Query
        return self._query_class

    def _query(self, relation):
        """Creates a new Query."""
        return self.query_class(relation)

    def _execute_query(self, query,return_type=lambda x: x, scalar=False):
        result = self._session.query(query)
        return return_type(result) if scalar else map(return_type, result)


class EmailerMixin(object):
    """Mixin class for services that send email. The constructor must
    set a ``_mailer`` attribute."""

    def _send_mail(self, sender, receivers, subject, message, attachements):
        raise NotImplementedError


import warnings


class PublisherMixin(object):
    """Mixin class for services that send email. The constructor must
    set a ``_publisher`` attribute."""

    def _publish_event(self, event, *args, **kwargs):
        try:
            publisher = self._publisher
        except AttributeError:
            service_name = type(self).__name__
            event_name = type(event).__name__
            warnings.warn(
                "{0} was initialized without a publisher. Listeners wi"
                "ll not be notified of emitted event {1}. Make sure th"
                "e service constructor sets a `_publisher` attribute h"
                "olding the event publisher instance".format(service_name,
                    event_name), RuntimeWarning, stacklevel=2
            )
        else:
            publisher.publish(event, *args, **kwargs)
