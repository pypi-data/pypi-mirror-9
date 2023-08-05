import abc

from libtng import six


class Checksum(six.with_metaclass(abc.ABCMeta)):
    """
    Base class for all checksum algorithms.
    """

    @abc.abstractproperty
    def value_type(self):
        raise NotImplementedError

    @abc.abstractproperty
    def valid_checksum(self):
        raise NotImplementedError

    def is_valid(self, value):
        """
        Validates if `value` passes the checksum.
        """
        if not value:
            raise ValueError("Input value may not evaluate to False.")
        return self.checksum(value) == self.valid_checksum

    @abc.abstractmethod
    def checksum(self, value):
        """
        Calculate a checksum for the specified value.
        """
        raise NotImplementedError

    @abc.abstractmethod
    def check_digit(self, value):
        """
        Returns the check digit that should be appended to `value`
        to pass the checksum.
        """
        raise NotImplementedError

    def get(self, value):
        """
        Mutate `value` so that it passes the checksum algorithm.

        Returns:
            str
        """
        check_digit = self.check_digit(value)
        return self.value_type(six.text_type(value) \
            + six.text_type(check_digit))