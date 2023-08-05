import abc

from libtng import six


class BaseHandler(six.with_metaclass(abc.ABCMeta)):
    """
    Base class for backend connection handlers.
    """

    @abc.abstractproperty
    def default_port(self):
        pass