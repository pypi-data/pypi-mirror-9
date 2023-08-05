from libtng.http.exceptions.base import HttpException


class UnprocessableEntity(HttpException):
    status_code = 422
    error_code = 'UNPROCESSABLE_ENTITY'
    default_params = {
        'error_code' : error_code,
        'message'   : (
            "The server was unable to process the contained instructions."
        ),
        'detail': '',
        'hint': ''
    }