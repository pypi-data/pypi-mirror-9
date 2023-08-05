import math
import re
try:
    import functools
    map = functools.map
except AttributeError:
    del functools


NON_ALPHANUMERIC = set(
    [chr(i) for i in range(32,127) if not re.match('[a-zA-Z0-9]', chr(i))])


class RawPassword(object):
    """Represents a raw, unhashed password."""
    classifiers = [
        lambda x: 26 if re.match('[a-z]', x) else 0,
        lambda x: 26 if re.match('[A-Z]', x) else 0,
        lambda x: 10 if re.match('[0-9]', x) else 0,
        lambda x: len(NON_ALPHANUMERIC) \
            if (set(x) & NON_ALPHANUMERIC) else 0
    ]

    @property
    def entropy(self):
        return math.log(self._get_pool_size(), 2) * len(self)

    def __init__(self, raw_password):
        self._raw_password = raw_password

    def _get_pool_size(self):
        # Returns the size of the character pool
        return sum(map(lambda x: x(self._raw_password), self.classifiers))

    def __len__(self):
        return len(self._raw_password)

    def __repr__(self):
        return "<RawPassword: ********>"

    def __str__(self):
        return "********"


