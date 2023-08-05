from libtng.http.base import HttpResponse
from libtng import six


class Redirect(HttpResponse):
    default_status_code = 307

    def __init__(self, url, *args, **kwargs):
        super(HttpResponseNotAllowed, self).__init__(*args, **kwargs)
        self.headers['Location'] = url