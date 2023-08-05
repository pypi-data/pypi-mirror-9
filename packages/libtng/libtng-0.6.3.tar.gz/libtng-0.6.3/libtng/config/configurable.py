import abc

from libtng import six


class Configurable(six.with_metaclass(abc.ABCMeta)):
    """
    Represents a configurable object.
    """

    @abc.abstractmethod
    def teardown(self):
        """Tears down the configuration."""
        raise NotImplementedError