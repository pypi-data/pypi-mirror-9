from libtng.http.exceptions.base import HttpException


class NotFound(HttpException):
    status_code = 404
    error_code = 'NOT_FOUND'
    default_params = {
        'error_code' : error_code,
        'message'   : (
            "The server has not found anything matching the Request-UR"
            "I. No indication is given of whether the condition is tem"
            "porary or permanent."
        ),
        'detail': '',
        'hint': ''
    }