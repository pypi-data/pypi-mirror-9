from libtng.http.base import HttpResponse
from libtng import six


class HttpResponseNotAllowed(HttpResponse):
    default_status_code = 405

    def __init__(self, permitted_methods, *args, **kwargs):
        super(HttpResponseNotAllowed, self).__init__(*args, **kwargs)
        self.headers['Allow'] = ', '.join(map(six.binary_type, permitted_methods))