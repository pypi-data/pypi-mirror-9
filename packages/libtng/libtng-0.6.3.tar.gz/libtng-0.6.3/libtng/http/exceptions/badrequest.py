from libtng.http.exceptions.base import HttpException


class BadRequest(HttpException):
    status_code = 400
    error_code = 'BAD_REQUEST'
    default_params = {
        'error_code' : error_code,
        'message'   : (
            "The request could not be understood by the server due to "
            "malformed syntax. The client SHOULD NOT repeat the reques"
            "t without modifications."
        ),
        'detail': '',
        'hint': ''
    }