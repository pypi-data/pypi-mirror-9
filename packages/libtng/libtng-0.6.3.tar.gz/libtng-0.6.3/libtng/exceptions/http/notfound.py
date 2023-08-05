from libtng.exceptions.http.base import HttpException


class NotFound(HttpException):
    status_code = 404
    default_params = {
        'error' : 'NOT_FOUND',
        'msg'   : (
            "The server has not found anything matching the Request-UR"
            "I. No indication is given of whether the condition is tem"
            "porary or permanent."
        )
    }