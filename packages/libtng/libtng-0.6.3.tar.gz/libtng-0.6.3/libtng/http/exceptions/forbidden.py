from libtng.http.exceptions.base import HttpException


class Forbidden(HttpException):
    status_code = 403
    error_code = 'FORBIDDEN'
    default_params = {
        'error_code' : error_code,
        'message'   : (
            "The server understood the request, but is refusing to ful"
            "fill it. Authorization will not help and the request SHOU"
            "LD NOT be repeated."
        ),
        'detail': '',
        'hint': ''
    }
