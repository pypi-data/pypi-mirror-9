import abc

from libtng import six


class Serializer(six.with_metaclass(abc.ABCMeta)):
    class DeserializationError(ValueError):
        pass

    class SerializationError(ValueError):
        pass


    @abc.abstractmethod
    def serialize(self, obj, *args, **kwargs):
        """Serializes `obj`. Positional and keyword arguments
        must be forwarded to the underlying serializer implementation.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def deserialize(self, raw_data, *args, **kwargs):
        """Deseriaizes `raw_data` into a Python object."""
        raise NotImplementedError
