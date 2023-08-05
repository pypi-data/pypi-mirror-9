import abc

from libtng import six


class Mappable(six.with_metaclass(abc.ABCMeta)):
    """
    A conigurable mappable type.
    """

    def add_to_mapper(self, mapper, *args, **kwargs):
        """
        Adds the configurable to it's `mapper`.
        """
        return mapper.map(self, *args, **kwargs)