import copy
import abc

from libtng import six


class Authorization(object):
    """
    Represents the contents of an HTTP ``Authorization``
    header.
    """

    def __init__(self, scheme, params):
        """
        Initializes a new :class:`Authorization` instance.

        Args:
            scheme (str): a string specifying the authentication
                scheme used.
            params: the parameters provided in the ``Authorization``
                header.
        """
        self._scheme = scheme
        self._params = params

    def as_dict(self):
        """Return the contents of the `` Authorization`` header as a
        Python dictionary.
        """
        params = copy.deepcopy(self._params)
        params['scheme'] = self._scheme
        return params

    def __iter__(self):
        return iter([self._scheme, self._params])



class InvalidScheme(Exception):

    def __init__(self, scheme, header):
        self.scheme = scheme
        self.header = header


class Scheme(six.with_metaclass(abc.ABCMeta)):

    @abc.abstractproperty
    def scheme_name(self):
        raise NotImplementedError

    def parse(self, header):
        name, content = header.spit(' ', 1)
        if name != self._name:
            raise InvalidScheme(self, header)
        return self.parse_content(content)

    @abc.abstractmethod
    def parse_content(self):
        raise NotImplementedError