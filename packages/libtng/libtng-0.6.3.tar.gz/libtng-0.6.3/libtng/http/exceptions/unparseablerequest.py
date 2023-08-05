from libtng.http.exceptions.badrequest import BadRequest


class UnparseableRequest(BadRequest):
    status_code = 400
    error_code = 'UNPARSEABLE_REQUEST'
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

    def __init__(self, expected, *args, **kwargs):
        BadRequest.__init__(self, *args, **kwargs)
        self.hint = "Unable to parse the request body. Expected: {0}".format(expected)

    def get_hint(self):
        return self.hint