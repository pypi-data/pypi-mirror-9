from libtng.http.exceptions.base import HttpException


class ServiceUnavailable(HttpException):
    status_code = 400
    error_code = 'SERVICE_NOT_AVAILABLE'
    default_params = {
        'error_code' : error_code,
        'message'   : (
            "The server is currently unable to handle the request due "
            "to a temporary overloading or maintenance of the server."
        ),
        'detail': '',
        'hint': ''
    }