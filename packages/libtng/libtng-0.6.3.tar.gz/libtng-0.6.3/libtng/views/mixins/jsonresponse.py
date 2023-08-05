import json

from libtng.http import HttpResponse


class JsonResponseMixin(object):

    def render_to_response(self, data, status=200, indent=4):
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
        serialized = data.serialize(indent=indent) if hasattr(data, 'serialize')\
            else json.dumps(data, indent=4, ensure_ascii=True)
        return HttpResponse(serialized + "\n", status=status, mimetype="application/json")