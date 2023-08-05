"""
Wrappers around :mod:`sqlalchemy` objects.
"""
import collections

import sqlalchemy

from libtng.functional import cached_property


def _titlize(value):
    return re.sub('[\W\B]', ' ').title().replace(' ','')


def _construct_row_class(relation):
    name = "{0}".format(relation.name.title())
    return collections.namedtuple(name, [x.name for x in relation.columns])


class Relation(sqlalchemy.Table):
    """
    Represents a base or virtual relation.
    """

    @cached_property
    def row_class(self):
        """
        Returns a :class:`namedtuple` wrapping the columns of the result set.
        """
        return _construct_row_class(self)
