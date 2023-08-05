


class URLProvider(object):

    def __init__(self, builder):
        self._map = None
        self._rules = []
        self._urls = []
        self._endpoints = {}
        self._builder = builder

    def match(self, environ):
        """Match an URL to the WSGI environment."""
        urls = self.bind_to_environ(environ)
        endpoint, kwargs = urls.match()
        return self._endpoints[endpoint], endpoint, kwargs

    def bind_to_environ(self, environ):
        """Binds the URL map to a WSGI environment."""
        if self._map is None:
            self.build_map()
        return self._map.bind_to_environ(environ)

    def register_url(self, url, endpoint):
        """Register an URL at the specified endpoint."""
        self._urls.append([url, {'endpoint': endpoint}])

    def register_endpoint(self, endpoint, func):
        """Registers a callable as a named endpoint."""
        self._endpoints[endpoint] = func

    def build_map(self):
        if self._map is not None:
            raise RuntimeError("URL mapping already built.")
        self._map = self._builder(self._urls, self._endpoints)