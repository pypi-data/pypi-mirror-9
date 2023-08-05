import abc

from libtng import six


class BaseHeader(six.with_metaclass(abc.ABCMeta)):
    """Base class for all header types."""

    @classmethod
    def as_string(cls, *args, **kwargs):
        """
        Instantiate a new :class:`BaseHeader` object with the specified
        parameters and return it's string value.
        """
        instance = cls(*args, **kwargs)
        return instance.render_to_string()

    @abc.abstractmethod
    def render_to_string(self):
        """Renders the header to the actual value included in the
        response to the downstream clients.
        """
        raise NotImplementedError