import abc


class WSGIApplication(metaclass=abc.ABCMeta):
    """Base interface for WSGI applications."""
    response_class  = abc.abstractproperty()
    request_class   = abc.abstractproperty()

    def accept(self, environ, start_response):
        """Accepts the incoming environment and calls `start_response`
        to start streaming the response to the client.
        """
        request = self.request_factory(environ)
        try:
            view_name, func, kwargs = self.match(environ)
        except Exception as e:
            response = self.respond_404(request, e)
            return response(environ, start_response)

        try:
            response = func(request, **kwargs)
        except Exception as e:
            if not hasattr(e, 'get_response'):
                raise
            response = e.get_response(environ=environ)

        return response(environ, start_response)

    @abc.abstractmethod
    def request_factory(self, environ):
        """Create a new :class:`Request` object from the WSGI
        environment.
        """
        raise NotImplementedError("Subclasses must override this method.")

    @abc.abstractmethod
    def match(self, environ):
        """Take the incoming WSGI environment and return a three-tuple
        holding the endpoint name, the callable and the parameters from
        the resource URI.
        """
        raise NotImplementedError("Subclasses must override this method.")

    @abc.abstractmethod
    def respond_404(self, request, exception):
        """Returns a 404 response."""
        raise NotImplementedError("Subclasses must override this method.")

    def __call__(self, environ, start_response):
        return self.accept(environ, start_response)
