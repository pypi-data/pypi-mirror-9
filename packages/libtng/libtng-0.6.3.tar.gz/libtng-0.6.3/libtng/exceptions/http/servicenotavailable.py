from libtng.exceptions.http.base import HttpException


class ServiceNotAvailable(HttpException):
    status_code = 503
    default_params = {
        'error' : 'SERVICE_NOT_AVAILABLE',
        'msg'   : (
            "The server is currently unable to handle the request due "
            "to a temporary overloading or maintenance of the server."
        )
    }