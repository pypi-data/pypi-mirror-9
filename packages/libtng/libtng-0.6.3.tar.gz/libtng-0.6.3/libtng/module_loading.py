import importlib
import sys

from libtng import six
from libtng.exceptions import ProgrammingError
from libtng.encoding import force_text


def import_string(dotted_path):
    """
    Import a dotted module path and return the attribute/class
    designated by the last name in the path. Raise :exc:`ImportError`
    if the import failed.

    Args:
        dotted_path: a string containing the fully-qualified path
            to an attribute in a Python module.

    Returns:
        object: the attribute specified by `dotted_path`.
    """
    dotted_path = force_text(dotted_path)
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        msg = "{0} doesn't look like a module path".format(dotted_path)
        six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])

    module = importlib.import_module(module_path)

    try:
        return getattr(module, class_name)
    except AttributeError:
        msg = 'Module "{0}" does not define a "{1}" attribute/class'.format(
            dotted_path, class_name)
        six.reraise(ImportError, ImportError(msg), sys.exc_info()[2])


def import_by_path(dotted_path, error_prefix=''):
    """
    Import a dotted module path and return the attribute/class
    designated by the last name in the path.

    Args:
        dotted_path: a string containing the fully-qualified path
            to an attribute in a Python module.

    Returns:
        object: the attribute specified by `dotted_path`.

    Raises:
        ProgrammingError: could not import the module.
    """
    try:
        module_path, class_name = dotted_path.rsplit('.', 1)
    except ValueError:
        raise ProgrammingError("{0}{1} doesn't look like a module path"\
            .format(error_prefix, dotted_path))
    try:
        module = importlib.import_module(module_path)
    except ImportError as e:
        msg = '{0}Error importing module {1}: "{2}"'.format(
            error_prefix, module_path, e)
        six.reraise(ProgrammingError, ProgrammingError(msg),
                    sys.exc_info()[2])
    try:
        attr = getattr(module, class_name)
    except AttributeError:
        raise ProgrammingError(
            '{0}Module "{1}" does not define a "{2}" attribute/class'\
                .format(error_prefix, module_path, class_name)
        )
    return attr
