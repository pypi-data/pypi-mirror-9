


class CommandViewMixin(object):
    """
    Mixin  class that exposes various methods and attributes
    for processing :class:`libtng.cqrs.Command` instances.
    """

    #: A :class:`libtng.cqrs.Command` subclass representing the command
    #: to execute.
    command_type = None

    #: A :class:`str` specifiyng the request method; must be ``PUT``,
    #: or ``POST``.
    request_method = 'PUT'

    #: Gateway handling the command.
    gateway = None

    #: The defalt mimetype for command endpoints is ``application/json``.
    default_mimetype = 'application/json'


    def get_command(self, request):
        """
        Returns an instance of :attr:`CommandViewMixin.command_type`.
        """
        return self.command_type(**self.parse_request_body(request))

    def accept(self, request, gateway_response):
        """
        Generate a HTTP response indicating that the command
        has been accepted.

        Args:
            request: the incoming HTTP request.
            response: the response from the gateway processing the
                command.

        Returns:
            libtng.http.Response
        """
        response = self.response_factory(status_code=206)
        self.process_gateway_response(gateway_response,
            response)
        return response

    def reject(self, request, exception):
        """
        Generate a HTTP response indicating that the command
        has been rejected.

        Args:
            request: the incoming HTTP request.
            exception: the exception instance that caused the rejection of
                the command. Must inherit from
                :class:`libtng.cqrs.UnprocessableCommandException`.

        Returns:
            libtng.http.Response
        """
        raise NotImplementedError("Subclasses must override this method.")

    def put(self, request, *args, **kwargs):
        """
        Processes an incoming HTTP request representing a command and
        returns a descriptive response indicating wether the command
        was accepted or rejected.

        Args:
            request: the incoming HTTP request.

        Returns:
            libtng.http.Response
        """
        try:
            command = self.get_command()
            response = self.accept(request, self.to_gateway(command))
        except cqrs.UnprocessableCommandException as e:
            response = self.reject(request, e)
        return response

    def to_gateway(self, command):
        """
        Dispatches the command to it's handler using the gateway specified
        on the view object.
        """
        return self.gateway.put(command)

    def process_gateway_response(self, gateway_response, response):
        """
        Hook to modify the HTTP response returned to the client based
        on the result from the command gateway.

        The default implementation leaves the HTTP response unmodified.

        Args:
            gateway_response: the response returned from the command
                gateway.
            response (libtng.http.Response): response object to be
                sent to the client.

        Returns:
            None
        """
        pass