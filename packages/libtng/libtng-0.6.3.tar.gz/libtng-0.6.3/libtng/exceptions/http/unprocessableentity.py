from libtng.exceptions.http.base import HttpException


class UnprocessableEntity(HttpException):
    status_code = 422
    default_params = {
        'error' : 'UNPROCESSABLE_ENTITY',
        'msg'   : (
            "The was unable to process the contained instructions."
        )
    }