import operator

from libtng.ioc.provider import _provider
from libtng.functional import SimpleLazyObject
from libtng import six


def new_method_proxy(func):
    def inner(self, *args):
        return func(_provider.get(self.key), *args)
    return inner


class DependencyMeta(type):

    def __instancecheck__(self, other):
        return isinstance(_provider.get(self.key), type(other))




class Dependency(six.with_metaclass(DependencyMeta)):
    """
    Represents a dependency declared by a system component.
    """

    def __init__(self, key, methods=None, type=None, description=None,
        attributes=None, alternatives=None):
        """
        Initialize a new :class:`Dependency` instance.

        Args:
            key (str): the key identifying the dependency.
            methods (list): specifies the methods that a
                provided :class:`~libtng.ioc.Feature` MUST
                expose.
            attributes (list): specifies the attributes that a
                provided :class:`~libtng.ioc.Feature` MUST
                expose.
            alternatives (list): specifies alternatives.
        """
        self.key = key
        self._methods = methods or []
        self._attributes = attributes or []
        self._is_valid = False
        self._type = type
        self._description = description
        self._alternatives = alternatives or []

    def contribute_to_class(self, cls, attname):
        setattr(cls, attname, self)

    if six.PY3:
        __bytes__ = new_method_proxy(bytes)
        __str__ = new_method_proxy(str)
    else:
        __str__ = new_method_proxy(str)
        __unicode__ = new_method_proxy(unicode)

    __getattr__ = new_method_proxy(getattr)

    # For compatibility with abc.ABCMeta
    __isabstractmethod__ = False

    # Return a meaningful representation of the lazy object for debugging
    # without evaluating the wrapped object.
    def __repr__(self):
        try:
            return _provider.get(self.key).__repr__()
        except LookupError:
            return '<Dependency: {0} (missing)>'.format(self.key)

    def __call__(self, *args, **kwargs):
        return _provider.get(self.key)(*args, **kwargs)

    # Need to pretend to be the wrapped class, for the sake of objects that
    # care about this (especially in equality tests)
    __class__ = property(new_method_proxy(operator.attrgetter("__class__")))
    __eq__ = new_method_proxy(operator.eq)
    __ne__ = new_method_proxy(operator.ne)
    __hash__ = new_method_proxy(hash)
    __bool__ = new_method_proxy(bool)       # Python 3
    __nonzero__ = __bool__                  # Python 2



