from libtng.exceptions.http.base import HttpException


class InternalServerError(HttpException):
    status_code = 500
    default_params = {
        'error' : 'INTERNAL_SERVER_ERROR',
        'msg'   : (
            "The server encountered an unexpected condition which prev"
            "ented it from fulfilling the request."
        )
    }