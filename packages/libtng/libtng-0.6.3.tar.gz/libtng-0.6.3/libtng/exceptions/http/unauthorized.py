from libtng.exceptions.http.base import HttpException


class Unauthorized(HttpException):
    status_code = 401
    default_params = {
        'error' : 'UNAUTHORIZED',
        'msg'   : (
            "The request requires user authentication. The response MU"
            "ST include a WWW-Authenticate header field (section 14.47"
            ") containing a challenge applicable to the requested reso"
            "urce. The client MAY repeat the request with a suitable A"
            "uthorization header field (section 14.8). If the request "
            "already included Authorization credentials, then the 401 "
            "response indicates that authorization has been refused fo"
            "r those credentials. If the 401 response contains the sam"
            "e challenge as the prior response, and the user agent has"
            " already attempted authentication at least once, then the"
            " user SHOULD be presented the entity that was given in th"
            "e response, since that entity might include relevant diag"
            "nostic information. HTTP access authentication is explain"
            "ed in \"HTTP Authentication: Basic and Digest Access Auth"
            "entication\""
        )
    }