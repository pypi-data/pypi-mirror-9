from threading import local
import abc

import six


_data = local()



class Activatable(six.with_metaclass(abc.ABCMeta)):
    """
    Base class for thread-local activatables, such as
    the current user, current timezone, current locale,
    et al.
    """

    @abc.abstractproperty
    def local_name(self):
        return None

    def __init__(self, value, *args, **kwargs):
        self.value = value

    def __enter__(self, *args, **kwargs):
        self.old = getattr(_data, self.local_name, None)
        setattr(_data, self.local_name, self.value)
        self.on_enter()
        return self

    def on_enter(self):
        """
        Callback invoked when entering the context.
        """
        pass

    def on_exit(self, failed=False):
        """
        Callback invoked just prior to returning when
        exiting the context.

        :params failed:
            a :class:`bool` indicating if an exception
            occurred in the context.
        """
        pass

    def on_fail(self, exc_type, exc_instance, tb):
        """
        Callback invoked on faillure.
        """
        pass

    def __exit__(self, exc_type, exc_instance, tb):
        setattr(_data, self.local_name, self.old)
        if exc_type is not None:
            self.on_fail(exc_type, exc_instance, tb)
        self.on_exit(failed=exc_type is not None)


def activatable_factory(key, cls=None):
    """
    Factory function to create activatables.
    """
    bases = (Activatable,)
    if cls is not None:
        bases += (cls,)
    cls =  type(key, bases, {'local_name': key})
    return lambda value, *args, **kwargs: cls(value, *args, **kwargs)