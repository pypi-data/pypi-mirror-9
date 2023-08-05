import re
import collections
import json

from django.http import HttpResponse
from django.core.handlers.wsgi import WSGIRequest
from werkzeug.datastructures import EnvironHeaders
from werkzeug.urls import url_decode
from werkzeug._compat import wsgi_get_bytes
from werkzeug.datastructures import ImmutableMultiDict
from werkzeug.http import parse_date
from werkzeug.http import http_date
from werkzeug.http import parse_accept_header
from werkzeug.datastructures import MIMEAccept
from werkzeug.datastructures import CharsetAccept
from werkzeug.datastructures import LanguageAccept

from libtng.http.authorization import parse_authorization_header
from libtng.functional import cached_property

# Mimic Werkzeug API for Django
# Imitates werkzeug request
class DjangoWSGIRequest(WSGIRequest):

    #: the class to use for `args` and `form`.  The default is an
    #: :class:`~werkzeug.datastructures.ImmutableMultiDict` which supports
    #: multiple values per key.  alternatively it makes sense to use an
    #: :class:`~werkzeug.datastructures.ImmutableOrderedMultiDict` which
    #: preserves order or a :class:`~werkzeug.datastructures.ImmutableDict`
    #: which is the fastest but only remembers the last key.  It is also
    #: possible to use mutable structures, but this is not recommended.
    #:
    #: .. versionadded:: 0.6
    parameter_storage_class = ImmutableMultiDict

    #: the charset for the request, defaults to utf-8
    charset = 'utf-8'

    #: the error handling procedure for errors, defaults to 'replace'
    encoding_errors = 'replace'

    header_pattern = re.compile('(\w+)[:=] ?"?([\w\s\d\.\-\_\:]+)"?')

    #: The names to use when the HTTP ``Basic`` authentication scheme
    #: is used.
    basic_auth_names = ['client_id', 'client_secret']

    @property
    def authorization(self):
        """Parses the Authorization header and returns a
        :class:`~libtng.http.authorization.Authorization`
        instance, or ``None`` if no header was present.

        May raise a :exc:`ValueError` if the contents
        of the ``Authorization`` header could not be
        parsed.
        """
        scheme, params = None, {}
        try:
            value = self.headers['Authorization']
        except KeyError:
            return None
        else:
            return parse_authorization_header(value)

    @property
    def url_charset(self):
        """The charset that is assumed for URLs.  Defaults to the value
        of :attr:`charset`.

        .. versionadded:: 0.6
        """
        return self.encoding

    @cached_property
    def headers(self):
        """The headers from the WSGI environ as immutable
        :class:`~werkzeug.datastructures.EnvironHeaders`.
        """
        return EnvironHeaders(self.environ)

    @cached_property
    def form(self):
        return self.POST

    @cached_property
    def args(self):
        """The parsed URL parameters.  By default an
        :class:`~werkzeug.datastructures.ImmutableMultiDict`
        is returned from this function.  This can be changed by setting
        :attr:`parameter_storage_class` to a different type.  This might
        be necessary if the order of the form data is important.
        """
        return url_decode(wsgi_get_bytes(self.environ.get('QUERY_STRING', '')),
                          self.url_charset, errors=self.encoding_errors,
                          cls=self.parameter_storage_class)


    @cached_property
    def origin(self):
        """The IP address from which the incoming request originates."""
        return self.headers['Origin']

    def json(self):
        return json.loads(self.body)

    @property
    def files(self):
        return self.FILES

    @property
    def date(self):
        return parse_date(self.headers.get('Date')) or http_date()

    #//////////////////////////////////////////////////////////////////
    #// werkzeug.wrappers.AcceptMixin
    #//////////////////////////////////////////////////////////////////
    @cached_property
    def accept_mimetypes(self):
        """List of mimetypes this client supports as
        :class:`~werkzeug.datastructures.MIMEAccept` object.
        """
        return parse_accept_header(self.environ.get('HTTP_ACCEPT'), MIMEAccept)

    @cached_property
    def accept_charsets(self):
        """List of charsets this client supports as
        :class:`~werkzeug.datastructures.CharsetAccept` object.
        """
        return parse_accept_header(self.environ.get('HTTP_ACCEPT_CHARSET'),
                                   CharsetAccept)

    @cached_property
    def accept_encodings(self):
        """List of encodings this client accepts.  Encodings in a HTTP term
        are compression encodings such as gzip.  For charsets have a look at
        :attr:`accept_charset`.
        """
        return parse_accept_header(self.environ.get('HTTP_ACCEPT_ENCODING'))

    @cached_property
    def accept_languages(self):
        """List of languages this client accepts as
        :class:`~werkzeug.datastructures.LanguageAccept` object.

        .. versionchanged 0.5
           In previous versions this was a regular
           :class:`~werkzeug.datastructures.Accept` object.
        """
        return parse_accept_header(self.environ.get('HTTP_ACCEPT_LANGUAGE'),
                                   LanguageAccept)


    def accept_visitor(self, visitor):
        """
        Accepts a visitor.
        """
        return visitor.visit(self)

# Monkey patch the HttpResponse object to expose
# a `headers` attribute.
HttpResponse.headers = property(lambda self: self)