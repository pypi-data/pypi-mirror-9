from __future__ import unicode_literals
import abc

import logging
from functools import update_wrapper

from libtng import http
from libtng.decorators import classonlymethod
from libtng import six
from libtng.exceptions.http import RequestMethodNotAllowed
from libtng.exceptions.http import InternalServerError
from libtng.exceptions.http import HttpException


class ContextMixin(six.with_metaclass(abc.ABCMeta)):
    """
    A default context mixin that passes the keyword arguments received by
    get_context_data as the template context.
    """

    def get_context_data(self, **kwargs):
        if 'view' not in kwargs:
            kwargs['view'] = self
        return kwargs


class View(six.with_metaclass(abc.ABCMeta)):
    """
    Intentionally simple parent class for all views. Only implements
    dispatch-by-method and simple sanity checking.
    """
    mimetype = "text/html"
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
    catch_errors = False
    response_class = http.HttpResponse
    publisher_class = None

    def __init__(self, **kwargs):
        """
        Constructor. Called in the URLconf; can contain helpful extra
        keyword arguments, and other things.
        """
        # Go through keyword arguments, and either save their values to our
        # instance, or raise an error.
        for key, value in six.iteritems(kwargs):
            setattr(self, key, value)

    @classonlymethod
    def as_view(cls, **initkwargs):
        """
        Main entry point for a request-response process.
        """
        # sanitize keyword arguments
        for key in initkwargs:
            if key in cls.http_method_names:
                raise TypeError("You tried to pass in the {0} method name as a "
                                "keyword argument to {1}(). Don't do that."\
                                    .format(key, cls.__name__))
            if not hasattr(cls, key):
                raise TypeError("%s() received an invalid keyword %r. as_view "
                                "only accepts arguments that are already "
                                "attributes of the class." % (cls.__name__, key))

        def view(request, *args, **kwargs):
            self = cls(**initkwargs)
            if hasattr(self, 'get') and not hasattr(self, 'head'):
                self.head = self.get
            self.request = request
            self.args = args
            self.kwargs = kwargs
            return self.dispatch(request, *args, **kwargs)

        # take name and docstring from class
        update_wrapper(view, cls, updated=())

        # and possible attributes set by decorators
        # like csrf_exempt from dispatch
        update_wrapper(view, cls.dispatch, assigned=())
        return view

    def dispatch(self, request, *args, **kwargs):
        # Try to dispatch to the right method; if a method doesn't exist,
        # defer to the error handler. Also defer to the error handler if the
        # request method isn't on the approved list.
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(), self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        try:
            return handler(request, *args, **kwargs)
        except Exception as e:
            if not self.catch_errors:
                raise
            raise InternalServerError(mimetype=self.mimetype)

    def http_method_not_allowed(self, request, *args, **kwargs):
        # logger.warning('Method Not Allowed (%s): %s', request.method, request.path,
        #     extra={
        #         'status_code': 405,
        #         'request': self.request
        #     }
        # )
        #return http.HttpResponseNotAllowed(self._allowed_methods())
        raise RequestMethodNotAllowed(self._allowed_methods(), mimetype=self.mimetype)

    def options(self, request, *args, **kwargs):
        """
        Handles responding to requests for the OPTIONS HTTP verb.
        """
        response = http.HttpResponse()
        response.headers[six.binary_type('Allow')] = ', '.join(self._allowed_methods())
        response.headers[six.binary_type('Content-Length')] = '0'
        return response

    def _allowed_methods(self):
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]
