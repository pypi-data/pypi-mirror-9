import abc


class IUrlProvider(metaclass=abc.ABCMeta):
    """Base class for all URL providers."""

    @abc.abstractmethod
    def add(self, pattern, name, func):
        """Adds a new rule to the :class:`IUrlProvider`.

        Args:
            pattern (str): specifies the request URI format.
            name (str): a mnemonic identifier for the URL pattern.
            func: a callable that is passed a :class:`Request` object and
                the parameters specified by the URL pattern.

        Returns:
            None
        """
        raise NotImplementedError("Subclasses must override this method.")

    @abc.abstractmethod
    def bind(self, server_name, *args, **kwargs):
        """Bind a new :class:`WerkzeugUrlProvider` to the environment specified
        by the parameters.
        """
        raise NotImplementedError("Subclasses must override this method.")

    @abc.abstractmethod
    def match(self):
        """Matches the current environment to known URL patterns. Return
        a tuple containing the endpoint name, the view function and the
        view parameters.
        """
        raise NotImplementedError("Subclasses must override this method.")

