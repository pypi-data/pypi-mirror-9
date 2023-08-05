from libtng.exceptions.http.base import HttpException


class BadRequest(HttpException):
    status_code = 400
    default_params = {
        'error' : 'BAD_REQUEST',
        'msg'   : (
            "The request could not be understood by the server due to "
            "malformed syntax. The client SHOULD NOT repeat the reques"
            "t without modifications."
        )
    }