from werkzeug.routing import Map
from werkzeug.routing import Rule

from libtng.urlprovider.iurlprovider import IUrlProvider


class WerkzeugUrlProvider(IUrlProvider):
    urlmap      = property(lambda self: self.__map)
    controllers = property(lambda self: self.__controllers)

    def __init__(self, urlmap=None, controllers=None):
        self.__controllers = controllers or {}
        self.__map = urlmap or Map()
        self.__is_bound = urlmap is not None

    def add(self, pattern, name, func):
        self.controllers[name] = func
        self.urlmap.add(Rule(pattern, endpoint=name))

    def bind(self, server_name, *args, **kwargs):
        """Bind a new :class:`WerkzeugUrlProvider` to the environment specified
        by the parameters.
        """
        return WerkzeugUrlProvider(
                urlmap=self.urlmap.bind(server_name, *args, **kwargs),
                controllers=self.__controllers
        )

    def bind_to_environ(self, *args, **kwargs):
        return WerkzeugUrlProvider(
            urlmap=self.urlmap.bind_to_environ(*args, **kwargs),
            controllers=self.controllers
        )

    def match(self):
        """Matches the current environment to known URL patterns. Return
        a tuple containing the endpoint name, the view function and the
        view parameters.
        """
        endpoint, args = self.urlmap.match()
        return endpoint, self.__controllers[endpoint], args
