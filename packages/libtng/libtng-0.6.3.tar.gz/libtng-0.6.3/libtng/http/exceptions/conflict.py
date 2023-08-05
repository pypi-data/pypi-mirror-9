from libtng.http.exceptions.base import HttpException


class Conflict(HttpException):
    status_code = 409
    error_code = 'CONFLICT'
    default_params = {
        'error_code' : error_code,
        'message'   : (
            "The request could not be completed due to a conflict with"
            " the current state of the resource."
        ),
        'detail': '',
        'hint': ''
    }
