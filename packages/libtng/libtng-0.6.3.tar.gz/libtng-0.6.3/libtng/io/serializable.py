from libtng.encoding import force_bytes


class Serializable(object):
    """Specifie an interface for a serializable object."""

    @classmethod
    def deserialize(cls, serializer, serialized_object):
        """Rebuild the `serialized_object` using `serializer`."""
        raise NotImplementedError

    def serialize(self, serializer, *args, **kwargs):
        """Serializes the :class:`Serializable`.

        Args:
            serializer: a callable implementing the
                :class:`libtng.io.Serializer` interface.

        Returns:
            bytes
        """
        raise NotImplementedError