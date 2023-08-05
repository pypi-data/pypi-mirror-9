import operator

from libtng.exceptions import ProgrammingError


class ISpecification(object):
    """Abstract base class for specification types."""

    def is_satisfied(self, obj):
        """Returns a boolean indicating if the specification
        is satsified by the object.
        """
        if self.func is None:
            raise ProgrammingError(
                "Provide a callable to the constructor or override is"\
                "_satisfied()")
        return self.func(obj)

    def __and__(x, y):
        return CompositeSpecification(operator.and_, x, y)

    def __ne__(x, y):
        return CompositeSpecification(operator.ne, x, y)

    def __or__(x, y):
        return CompositeSpecification(operator.or_, x, y)

    def __xor__(x, y):
        return CompositeSpecification(operator.xor, x, y)


class Specification(ISpecification):
    """Declare a specification."""

    def __init__(self, func=None):
        self.func = func


class CompositeSpecification(ISpecification):
    """A specification consisting of multiple children."""

    def __init__(self, operator, x, y):
        self._operator = operator
        self._x = x
        self._y = y

    def is_satisfied(self, obj):
        return self._operator(self._x.is_satisfied(obj),
            self._y.is_satisfied(obj))