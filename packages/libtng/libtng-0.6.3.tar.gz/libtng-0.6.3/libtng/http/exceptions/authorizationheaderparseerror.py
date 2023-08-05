from libtng.http.exceptions.badrequest import BadRequest


class AuthorizationHeaderParseError(BadRequest):
    status_code = 400
    error_code = 'AUTHORIZATION_HEADER_PARSE_ERROR'
    default_params = {
        'error_code' : error_code,
        'message'   : (
            "The request could not be understood by the server due to "
            "malformed syntax. The client SHOULD NOT repeat the reques"
            "t without modifications."
        ),
        'detail': '',
        'hint': 'Could not parse the contents of the Authorization header.'
    }