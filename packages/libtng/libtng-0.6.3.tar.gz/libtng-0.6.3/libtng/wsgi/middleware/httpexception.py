from libtng.http.exceptions import HttpException
from libtng.http.exceptions import Unauthorized


class HttpExceptionMiddleware(object):
    """Catches and processes :mod:`libtng.http.exceptions`
    instances."""

    def process_exception(self, request, exception):
        if not issubclass(type(exception), HttpException):
            return
        return exception.render_to_response(request)