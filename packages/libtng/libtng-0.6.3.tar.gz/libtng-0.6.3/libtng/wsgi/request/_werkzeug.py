"""
WSGI request subclass.
"""
import json

from werkzeug.wrappers import Request
from werkzeug.wrappers import CommonRequestDescriptorsMixin

from libtng.functional import cached_property
from libtng.http.authorization import parse_authorization_header


class WSGIRequest(Request, CommonRequestDescriptorsMixin):

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
    def preferred_mimetype(self):
        """The preferred mimetype specified by the client."""
        return self.accept_mimetypes[0][0]\
            if ('Accept' in self.headers)\
            else None

    @property
    def body(self):
        return self.data

    @cached_property
    def json(self):
        return json.loads(self.body)