from __future__ import unicode_literals
import abc

import logging
from functools import update_wrapper

from libtng import http
from libtng.decorators import classonlymethod
from libtng import six
from libtng.http.exceptions import RequestMethodNotAllowed
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


class View(object):
    """
    Intentionally simple parent class for all views. Only implements
    dispatch-by-method and simple sanity checking.
    """
    content_type = None
    mimetype = "text/html"
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
    catch_errors = False
    response_class = None

    #: DDD event publisher.
    publisher_class = None

    default_body_parsers = {
        # 'application/json'      : JsonRequestBodyParser(),
        # 'application/yaml'      : YamlRequestBodyParser(),
        # 'application/x-yaml'    : YamlRequestBodyParser(),
        # 'text/yaml'             : YamlRequestBodyParser(),
        # 'text/x-yaml'           : YamlRequestBodyParser()
    }

    #: Request body parsers mapping from mimetype to parser instance.
    body_parsers = {}

    def __init__(self, **kwargs):
        """
        Constructor. Called in the URLconf; can contain helpful extra
        keyword arguments, and other things.
        """
        self.content_type = self.mimetype if not self.content_type\
            else self.content_type

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
        response_factory = getattr(self, 'render_to_response', self.response_factory)
        raise RequestMethodNotAllowed(self._allowed_methods(),
            mimetype=self.mimetype, response_factory=response_factory)

    def options(self, request, *args, **kwargs):
        """
        Handles responding to requests for the OPTIONS HTTP verb.
        """
        response = self.response_class()
        headers = getattr(response, 'headers', response)
        headers[six.binary_type('Allow')] = ', '.join(self._allowed_methods())
        headers[six.binary_type('Content-Length')] = '0'
        return response

    def _allowed_methods(self):
        return [m.upper() for m in self.http_method_names if hasattr(self, m)]

    @classmethod
    def allowed_methods(cls):
        return [m.upper() for m in cls.http_method_names if hasattr(cls, m)]

    def response_factory(self, content, *args, **kwargs):
        if 'mimetype' in kwargs:
            kwargs['content_type'] = kwargs.pop('mimetype')
        headers = kwargs.pop('headers', None) or {}
        response = self.response_class(content, *args, **kwargs)
        for header, value in headers.items():
            response.headers[header] = value
        return response