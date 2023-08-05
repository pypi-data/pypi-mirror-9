from libtng.http.exceptions.base import HttpException


class RangeNotSatisfiable(HttpException):
    status_code = 416
    error_code = 'REQUESTED_RANGE_NOT_SATISFIABLE'
    default_params = {
        'error_code' : error_code,
        'message'   : (
            "A server SHOULD return a response with this status code i"
            "f a request included a Range request-header field (RFC 26"
            "16 section 14.35), and none of the range-specifier values"
            " in this field overlap the current extent of the selected"
            " resource, and the request did not include an If-Range re"
            "quest-header field."
        ),
        'detail': '',
        'hint': ''
    }