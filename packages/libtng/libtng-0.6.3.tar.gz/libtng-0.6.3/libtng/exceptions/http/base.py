import copy
import json

from libtng.http import HttpResponse
from libtng.exceptions import ProgrammingError
from libtng.template import loader


class HttpException(Exception):
    """Base class for exceptions that should result in a
    certain HTTP response.
    """
    status_code = None
    default_params = {}
    default_mimetype = "text/html"
    template_name = None
    response_class = HttpResponse

    def __init__(self, params=None, mimetype=None, headers=None):
        """
        Initialize a new :class:`HttpException` instance.
        """
        if self.status_code is None:
            raise ProgrammingError("HttpException subclasses must define a `status_code` attribute.")
        self.params = copy.deepcopy(self.default_params)
        self.params.update(params or {})
        self.headers = headers
        self.mimetype = mimetype or self.default_mimetype

    def as_json(self):
        return json.dumps(self.params, indent=4, ensure_ascii=True)

    def get_template_names(self):
        """Return a list containing the template names"""
        return [self.template_name] if self.template_name\
            else ['{0}.html.j2'.format(self.status_code)]

    def get_response(self, mimetype=None, response_class=None):
        Response = response_class or self.response_class
        return Response(self.get_response_body(), status=self.status_code,
            headers=self.headers, mimetype=mimetype or self.mimetype)

    def get_response_body(self, mimetype=None):
        """Return a string containing the response body."""
        response = None
        mimetype = mimetype or self.mimetype
        if self.mimetype == 'text/html':
            t = loader.get_template(self.get_template_names())
        elif self.mimetype == 'application/json':
            response = json.dumps(self.params, indent=4, ensure_ascii=True)
        else:
            raise NotImplementedError
        return response

    def __call__(self, environ, start_response):
        raise NotImplementedError