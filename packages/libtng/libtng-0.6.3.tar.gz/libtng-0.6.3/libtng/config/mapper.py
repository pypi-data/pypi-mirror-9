import abc

from libtng import six


class Mapper(six.with_metaclass(abc.ABCMeta)):
    """
    A conigurable mapper type.
    """

    @abc.abstractmethod
    def map(self, mappable, *args, **kwargs):
        """
        Maps a :class:`libtng.config.Mappable` instance.

        Args:
            mappable (Mappable): the instance to map.
        """
        raise NotImplementedError