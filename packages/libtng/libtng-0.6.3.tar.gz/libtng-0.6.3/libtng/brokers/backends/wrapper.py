

class BrokerWrapper(object):
    """Specifies the methods that a message broker wrapper must support."""

    def get_connection_params(self):
        """Returns a dictionary holding the parameters needed to establish
        a connection with the message broker.
        """
        raise NotImplementedError

    def get_connection(self):
        """Return a native connection instance as provided by the underlying 
        library.
        """
        raise NotImplementedError
