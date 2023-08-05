from libtng.http.exceptions.base import HttpException


class InternalServerError(HttpException):
    status_code = 500
    error_code = 'INTERNAL_SERVER_ERROR'
    default_params = {
        'error_code' : error_code,
        'message'   : (
            "The server encountered an unexpected condition which prev"
            "ented it from fulfilling the request."
        ),
        'detail': '',
        'hint': ''
    }