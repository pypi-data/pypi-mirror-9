from werkzeug.wrappers import Response



class HttpResponseBase(Response):
    default_status_code = None

    def __init__(self, content=None, *args, **kwargs):
        if self.default_status_code:
            kwargs['status'] = self.default_status_code
        Response.__init__(self, content or '', *args, **kwargs)


class HttpResponse(HttpResponseBase):
    pass