import json
import warnings

from libtng.http.exceptions import UnparseableRequest


class JsonResponseMixin(object):
    indent = 4
    mimetype = "application/json"

    def render_to_response(self, data, status=None, indent=None,
        mimetype=None, status_code=200):
        """
        Serializes the response data to JSON and
        returns a Response object to the client.

        Args:
            data: a dictionary or serializable (class declares a
                'serialize()' method).

        Kwargs:
            status: an integer specifying the HTTP response code.
                Default is 200.
            indent: an integer specifying the number of indent in
                JSON output. Default is 4.

        Returns:
            HttpResponse: a :class:`~libtng.http.HttpResponse` object
                representing the response data returned to the client.
        """
        indent = indent or self.indent
        status_code = status or status_code
        if status:
            warnings.warn("The `status argument is deprecated, user `status_code`.",
                DeprecationWarning, stacklevel=2)
        serialized = data.serialize(indent=indent) if hasattr(data, 'serialize')\
            else json.dumps(data, indent=self.indent, ensure_ascii=True)
        return self.response_factory(serialized + "\n",
            status=status_code, mimetype=mimetype or self.mimetype)

    def get_request_data(self, request):
        """Parses JSON serialized data from the incoming request."""
        try:
            return request.json()
        except ValueError:
            raise UnparseableRequest("application/json",
                mimetype=self.mimetype, response_factory=self.render_to_response)
