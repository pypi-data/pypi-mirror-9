import abc

from libtng import six
from libtng.exceptions import NOTIMPLEMENTED_SUBCLASS


class BaseNegotiator(six.with_metaclass(abc.ABCMeta)):

    @abc.abstractmethod
    def get_parser(self, accept):
        """
        Get the parser for the request body based on the accept
        header.
        """
        raise NOTIMPLEMENTED_SUBCLASS


    @abc.abstractmethod
    def get_renderer(self, accept):
        """
        Get the renderer for the request body based on the accept
        header.
        """
        raise NOTIMPLEMENTED_SUBCLASS