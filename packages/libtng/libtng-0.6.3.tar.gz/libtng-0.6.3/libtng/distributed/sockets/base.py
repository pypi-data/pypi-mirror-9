


class Socket(object):
    """Specifies the basic socket interface.

    Basic usage is to provide the :class:`Socket` a socket factory,
    that is responsible for the underlying implementation of the    
    concept.
    """

    def __init__(self, socket_factory):
        """Initialize a new :class:`Socket` instance.

        Args:
            socket_factory: a callable that is responsible for
                creating the underlying socket imlpementation.
                This may be a vanilla Python socket, or other
                implementations such as ZeroMQ or Tornado.
        """
        self._socket = socket_factory()
        self._factory = socket_factory

    def recv(self, deserializer=lambda x: x, *args, **kwargs):
        """Receives data from the socket. All arguments after the
        `deserializer` keyword are forwared to the underlying implementation.

        Args:
            deserializer: adapts the received data to a desired data type.
        
        Returns:
            object

        Raises:
            EnvironmentError
        """
        return deserializer(self._socket.recv(*args, **kwargs))

    def send(self, data, serializer=lambda x: x, *args ,**kwargs):
        """Send data to the socket. All arguments after the `serializer`
        keyword are forwared to the underlying implementation.

        Args:
            data: the data to send to the socket.
            serializer: serializes the data for transmission over the
                wire.
    
        Returns:
            None

        Raises:
            EnvironmentError
        """
        self._socket.send(serializer(data), *args, **kwargs)


    def bind(self, addr):
        """Bind the socket to an address.

        This causes the socket to listen on a network port. Sockets on the
        other side of this connection will use ``Socket.connect(addr)`` to
        connect to this socket.

        Args:
            addr (str): The address string. This has the form  
                'protocol://interface:port', for example 'tcp://127.0.0.1:5555'

        Returns:
            None

        Raises:
            EnvironmentError: Cannot bind to address or already in use.
        """
        self._socket.bind(addr)

    def connect(self, addr):
        """Connects to the socket."""
        self._socket.connect(addr)

    def close(self):
        """Closes the socket."""
        self._socket.close()
