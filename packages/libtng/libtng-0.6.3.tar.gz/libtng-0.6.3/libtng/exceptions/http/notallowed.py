from libtng import six
from libtng.http import HttpResponseNotAllowed
from libtng.exceptions.http.base import HttpException


class RequestMethodNotAllowed(HttpException):
    status_code = 405
    default_params = {
        'error' : 'REQUEST_METHOD_NOT_ALLOWED',
        'msg'   : (
            "The method specified in the Request-Line is not allowed f"
            "or the resource identified by the Request-URI."
        )
    }
    response_class = HttpResponseNotAllowed

    def __init__(self, permitted_methods, *args, **kwargs):
        super(RequestMethodNotAllowed, self).__init__(*args, **kwargs)
        self.permitted_methods = permitted_methods

    def get_response(self, mimetype=None):
        permitted_methods = ', '.join(map(six.binary_type,
            self.permitted_methods))
        response = self.response_class(permitted_methods, self.get_response_body(),
            status=self.status_code, headers=self.headers, mimetype=mimetype or self.mimetype)
        return response