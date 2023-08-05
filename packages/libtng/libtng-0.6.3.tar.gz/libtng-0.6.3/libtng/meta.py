import inspect
import functools
import re


INTERNAL = []


# Calculate the verbose_name by converting from InitialCaps to "lowercase with spaces".
get_verbose_name = lambda class_name: re.sub('(((?<=[a-z])[A-Z])|([A-Z](?![A-Z]|$)))', ' \\1', class_name).lower().strip()


def notnull(keywords=None):
    """
    Method decorator that asserts that no positional arguments are
    ``None``.

    :func:`notnull` also checks keyword arguments specified by the
    `keywords` argument.
    """
    def decorator(method):
        @functools.wraps(method)
        def wrapped(*args, **kwargs):
            try:
                args_fail = (args.index(None)+1) if (None in args)\
                    else 0
                kwargs_fail = [x for x, y in kwargs.items() if (y is None)]
                if args_fail or kwargs_fail:
                    raise TypeError(
                        "{0} does not allow null arguments ({0}, {1})."\
                        .format(method.__name__), args_fail, kwargs_fail)
            except IndexError:
                pass
            return method(*args, **kwargs)
    return decorator



def internal(obj):
    if obj not in INTERNAL:
        INTERNAL.append(obj)
    return obj


def accepts_keyword_arguments(callable):
    """
    Return a bool indicating if the given `callable` accepts
    keyword arguments.
    """
    args, varargs, varkw, defaults = inspect.getargspec(callable)
    return varkw is not None


class DeclarativeBase(object):

    def __new__(cls, name, bases, attrs):
        return super(DeclarativeBase, cls).__new__(cls, name, bases, attrs)


class ImmutableAttribute(object):
    """
    Descriptor that does not allow setting or deleting
    an attribute.
    """

    def __init__(self, value):
        self.value = value

    def __get__(self, instance, cls):
        return self.value

    def __set__(self, value):
        raise AttributeError("Can't set attribute.")


class AnnotatedMethodDescriptor(object):
    """
    Annotate a method.

    Example:

        >>> from libtng.meta import annotate
        >>>
        >>> class Foo(object):
        ...
        ...     @annotate(bar='baz')
        ...     def annotated_method(self):
        ...         print "Hello world!"
        ...
        >>> obj = Foo()
        >>> hasattr(obj, 'bar')
        True

    """

    def __init__(self, func, **annotations):
        self.func = func
        for key, value in annotations.items():
            if key.startswith('_'):
                continue
            setattr(self, key, value)

    def __get__(self, instance, cls):
        return self.func

    def __call__(self, *args, **kwargs):
        return self.func(*args, **kwargs)

    def __repr__(self):
        return repr(self.func)


def annotate(**annotations):
    """
    Annotate an instance method.
    """
    def wrapped(func):
        return AnnotatedMethodDescriptor(func, **annotations)
    return wrapped

