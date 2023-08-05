from libtng.http.exceptions.unprocessableentity import UnprocessableEntity


class UnknownAuthorizationScheme(UnprocessableEntity, LookupError):
    status_code = 422
    error_code = 'UNKNOWN_AUTHORIZATION_SCHEME'
    default_params = {
        'error_code' : error_code,
        'message'   : (
            "The server was unable to process the contained instructions."
        ),
        'detail': '',
        'hint': 'The scheme specified in the Authorization header is unknown.'
    }