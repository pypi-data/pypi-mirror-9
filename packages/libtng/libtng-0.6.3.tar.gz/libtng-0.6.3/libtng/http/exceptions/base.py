import copy

from libtng.exceptions import ProgrammingError


class HttpException(Exception):
    """Base class for exceptions that should result in a
    certain HTTP response.
    """
    status_code = None
    default_params = {}
    default_mimetype = "text/html"

    @property
    def template_names(self):
        return map(lambda x: x.format(self.status_code), [
            "{0}.html","{0}.html.j2"])

    def __init__(self, params=None, mimetype=None, headers=None, response_factory=None,
        hint=None, detail=None, render_content=None):
        """
        Initialize a new :class:`HttpException` instance.
        """
        if self.status_code is None:
            raise ProgrammingError("HttpException subclasses must define a `status_code` attribute.")
        self.params = copy.deepcopy(self.default_params)
        self.params.update(params or {})
        self.headers = headers or {}
        self.mimetype = mimetype or self.default_mimetype
        self.response_factory = response_factory
        self.hint = hint
        self.detail = detail
        self.render_content = render_content

    def render_to_response(self, request, response_factory=None, mimetype=None):
        """
        Get the content for the HTTP response to the client.

        Args:
            request: the incoming WSGI request object.
            response_factory: optionally override the response factory
                provided to the constructor.
            mimetype: optionally override the mimetype specified at
                construction time.

        Returns:
            HttpResponse: returned by the response factory provided
                to the constructor.
            None: no response factory was provided to the constructor.
        """
        response_factory = response_factory or self.response_factory
        if response_factory is not None:
            response = response_factory(self.get_response_content(request),
                mimetype=mimetype or self.mimetype,
                status_code=self.status_code)
            for header, value in self.headers.items():
                response.headers[header] = value
            return response

    def get_params(self):
        """
        Returns the parameters specified to the exception constructor.
        """
        params = copy.deepcopy(self.params)
        params['status_code'] = self.status_code
        if self.hint:
            params['hint'] = self.get_hint()
        if self.detail:
            params['detail'] = self.detail
        return params

    def get_response_content(self, request):
        """
        Return the content of an outgoing response.
        """
        return self.get_params()

    def get_hint(self):
        return self.hint