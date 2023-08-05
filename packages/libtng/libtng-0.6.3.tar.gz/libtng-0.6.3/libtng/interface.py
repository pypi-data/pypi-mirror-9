"""
Conveniance functions for Abstract Base Classes.
"""
import abc

import six


class Interface(six.with_metaclass(abc.ABCMeta)):
    pass