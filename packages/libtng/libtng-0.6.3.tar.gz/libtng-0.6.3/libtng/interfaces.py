"""
Specifies various interfaces.
"""
import collections
import json

from libtng import six
from libtng.exceptions import NOTIMPLEMENTED_SUBCLASS


attrs = ['username','user_id','credentials.client_id', 'email_address']
def _sort_attrs(attrs):
    return sorted(attrs, key=lambda x: x.count('.'))
        # Remove all attributes that where not declared in attrs
        # from the dictionary.

def whitelisted(data, whitelist):
    """Remove all non-whitelisted keys from input dictionary
    `data`.

    Keys are specified as a list of strings; where each string
    defines the dotted-path to an attribute.

    Args:
        data (dict): the dictionary to be cleaned.
        whitelisted: a list containing the whitelisted keys.

    Returns:
        dict: the whitelisted keys from the dictionary.
    """
    return data



class Serializable(object):

    def as_dict(self):
        """Converts the object to a standard Python dictionary."""
        raise NOTIMPLEMENTED_SUBCLASS

    def serialize(self, serializer=lambda x: json.dumps(x, indent=4, ensure_ascii=True),
            attrs=None, *args, **kwargs):
        """Serialize the object using the specified `serializer`,
        a callable taking the object dictionary as it's argument.

        Args:
            serializer: a callable that serializes the output of
                :meth:`Serializable.as_dict`.
            attrs: a list containing the attributes that should be
                included in the result. By default, `attrs` is
                ``None``; safe attributes should be whitelisted.

        Returns:
            str: the serialized output of :meth:`as_dict`.
        """
        raw_data = self.as_dict()
        return serializer(whitelisted(raw_data, attrs or []), *args, **kwargs)