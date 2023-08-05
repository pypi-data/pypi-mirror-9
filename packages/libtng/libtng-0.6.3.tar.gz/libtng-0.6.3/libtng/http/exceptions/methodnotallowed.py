from libtng.http.exceptions.base import HttpException


class RequestMethodNotAllowed(HttpException):
    status_code = 405
    error_code = 'REQUEST_METHOD_NOT_ALLOWED'
    default_params = {
        'error_code' : error_code,
        'message'   : (
            "The method specified in the Request-Line is not allowed f"
            "or the resource identified by the Request-URI."
        ),
        'detail': '',
        'hint': ''
    }


    def __init__(self, allowed_methods, *args, **kwargs):
        HttpException.__init__(self, *args, **kwargs)
        if allowed_methods and 'hint' not in kwargs:
            self.hint = 'Allowed methods: {0}'.format(', '.join(allowed_methods))