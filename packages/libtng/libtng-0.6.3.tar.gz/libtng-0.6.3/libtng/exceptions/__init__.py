import operator
import errno

from libtng.encoding import force_text


NON_FIELD_ERRORS = '__all__'


class PermissionDenied(Exception):
    """
    Raised when a system agent tries to access a resource which is not
    exposed to him.
    """


class InvalidDataSourceName(ValueError):
    errno = errno.ENXIO


class AddressAlreadyInUse(EnvironmentError):
    errno = errno.EADDRINUSE



class FatalException(Exception):
    """Raises when a program exits non-gracefully."""

    def __init__(self, exception, message, errcode=1, *args, **kwargs):
        self.exception = exception
        self.message = message
        self.errcode = errcode
        self.args = args
        self.kwargs = kwargs

    def __str__(self):
        return self.message


class ValidationError(Exception):
    """
    Raises when the state of does not meet a certain criteria.
    """

    def __init__(self, message, code=None, params=None):
        """
        ValidationError can be passed any object that can be printed (usually
        a string), a list of objects or a dictionary.
        """
        if isinstance(message, dict):
            self.error_dict = message
        elif isinstance(message, list):
            self.error_list = message
        else:
            self.code = code
            self.params = params
            self.message = message
            self.error_list = [self]

    @property
    def message_dict(self):
        message_dict = {}
        for field, messages in self.error_dict.items():
            message_dict[field] = []
            for message in messages:
                if isinstance(message, ValidationError):
                    message_dict[field].extend(message.messages)
                else:
                    message_dict[field].append(force_text(message))
        return message_dict

    @property
    def messages(self):
        if hasattr(self, 'error_dict'):
            message_list = reduce(operator.add, self.error_dict.values())
        else:
            message_list = self.error_list

        messages = []
        for message in message_list:
            if isinstance(message, ValidationError):
                params = message.params
                message = message.message
                if params:
                    message %= params
            message = force_text(message)
            messages.append(message)
        return messages

    def __str__(self):
        if hasattr(self, 'error_dict'):
            return repr(self.message_dict)
        return repr(self.messages)

    def __repr__(self):
        return '{0}{1}'.format(
            type(self).__name__, self)

    def update_error_dict(self, error_dict):
        if hasattr(self, 'error_dict'):
            if error_dict:
                for k, v in self.error_dict.items():
                    error_dict.setdefault(k, []).extend(v)
            else:
                error_dict = self.error_dict
        else:
            error_dict[NON_FIELD_ERRORS] = self.error_list
        return error_dict


class ImproperlyConfigured(Exception):
    """
    Raised when a runtime configuration setting contains an
    illegal or invalid value.
    """
    pass


class IllegalStateException(RuntimeError):
    """
    Should be raised when an operation would lead to an invalid
    application state.
    """
    pass


class ResourceDoesNotExist(ValueError):
    """
    Base-class for exceptions to be raised when an entity
    is requested by it's `identifier` but it did not exist.
    """
    pass


class SuspiciousOperation(Exception):
    pass


NOTIMPLEMENTED_SUBCLASS = NotImplementedError("Subclasses must override this method.")


class ProgrammingError(Exception):
    """
    Raised when faulty programming led to an invalid state.
    """


class DuplicateResource(Exception):
    """
    Raises when a resource is being created that has a unique
    constraint on it.
    """



def unsupported_operand(operand, lhs, rhs):
    """
    Return a :exc:`TypeError` indicating invalid `operand`
    between `lhs` and `rhs`.

    :param operand:
        a string indicating the operand.
    :param lhs:
        the left-hand side of the equation.
    :param rhs:
        the right-hand side of the equation.
    """
    msg = "unsupported operand type(s) for {0}: '{1}' and '{2}'"\
        .format(operand, type(lhs).__name__, type(rhs).__name__)
    return TypeError(msg)


def object_has_no_attribute(instance, attname):
    """
    Return an :exc:`AttributeError` indicating that *instance*
    does not have attribute *attname*.

    :param instance:
        a Python object.
    :param attname:
        a :class:`str` holding the attribute name.
    """
    msg = "'{0}' object has no attribute '{1}'".format(type(instance), attname)
    return AttributeError(msg)