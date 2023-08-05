"""
Various string formatting functions.
"""
import unicodedata
import re

from libtng import six


def slugify(value, sep='-', ignored=None):
    """
    Converts to lowercase, removes non-word characters (alphanumerics and
    underscores) and converts spaces to hyphens. Also strips leading and
    trailing whitespace.
    """
    ignored = ''.join(map(re.escape, set(ignored or [])))
    if not isinstance(value, six.text_type):
        value = six.text_type(value)
    value = unicodedata.normalize('NFKD', value)\
        .encode('ascii', 'ignore').decode('ascii')
    value = re.sub('[^\w\s{0}{1}]'.format(re.escape(sep), ignored), '', value)\
        .strip()\
        .lower()
    return re.sub('[{0}\s]+'.format(re.escape(sep)), sep, value)