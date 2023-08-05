from sqlalchemy.orm import class_mapper
from sqlalchemy.sql.schema import UniqueConstraint
import sqlalchemy

from libtng.datastructures import OrderedSet
from libtng.db.relation.query import RelationQuery


class AlternateKey(object):
    """
    Represents an alternate key of a :class:`~libtng.db.relation.Relation`.
    """

    def __init__(self, cls, constraint):
        self._class = cls
        self._constraint = constraint
        self._mapper = class_mapper(cls)
        self._columns = [x for x in constraint.columns]

    def predicate(self, **kwargs):
        """
        Get a tuple of :class:`sqlalchemy.sql.expression.BinaryExpression`
        instances.
        """
        try:
            return tuple([(x==kwargs[x]) for x in self._columns])
        except KeyError:
            raise ColumnDoesNotExist("Not a primary attribute: {0}".format(e.args[0]))

    def __repr__(self):
        return 'AlternateKey({0})'.format(self._class.__name__)



class InstanceAlternateKey(AlternateKey):
    """
    Represents the primary key of a :class:`~libtng.db.relation.Relation`
    *instance*.
    """

    def __init__(self, instance, constraint):
        self._instance = instance
        AlternateKey.__init__(self, type(instance), constraint)

    def query(self):
        """
        Return a :class:`sqlalchemy.orm.Query` instance matching
        the tuple identified by :meth:`predicate`.

        :param session:
            a :class:`sqlalchemy.orm.session.Session` instance,
            identifying the database connection and session.
        :returns:
            :class:`libtng.db.relation.query.RelationQuery`
        """
        return RelationQuery(self._class).filter(self.predicate())

    def exists(self, session):
        """
        Returns a boolean indicating if the key is persistent.

        :param session:
            a :class:`sqlalchemy.orm.session.Session` instance,
            identifying the database connection and session.
        :returns:
            :class:`boolean`
        """
        return session.query(self.query().exists()).scalar()

    def update(self, returning=None):
        """
        Return a :class:`sqlalchemy.sql.dml.Update`
        object matching the tuple identified by the key.
        """
        return sqlalchemy.update(self._class)\
            .where(self.predicate())\
            .returning(*(returning or []))

    def as_tuple(self):
        """
        Return the primary key as an :class:`libtng.datastructures.OrderedSet`.

        .. note::
            all key attributes must be hashable to use :meth:`as_tuple`.
        """
        return OrderedSet([getattr(self._instance, x.key)
            for x in self._columns])

    def predicate(self, **kwargs):
        """
        Get a tuple of :class:`sqlalchemy.sql.expression.BinaryExpression`
        instances.
        """
        c = self._columns[0]
        p = c==getattr(self._instance, c.key)
        for c in self._columns[1:]:
            p &= c==getattr(self._instance, c.key)
        return p

    def is_valid(self):
        """
        Returns a boolean indicating if the key is valid.
        Since key attributes can never be ``NULL``, this simply
        asserts that all attributes are not ``None``.
        """
        return all([x is not None for x in self.as_tuple()])

    def get_object(self, session):
        """
        Get the object identified by :class:`Identifier` from
        the session.
        """
        return session.query(self._class).filter(self.predicate()).one()

    def set_identifying_attributes(self, other):
        """
        Set identifying attributes to `other`. Primarily used for updating
        the primary key of an object.
        """
        map(lambda x: setattr(other, x.key, getattr(self._instance, x.key)), self._columns)

    def __repr__(self):
        return 'InstanceAlternateKey({0})'.format(self._class.__name__)

    def __iter__(self):
        return iter(self.as_tuple())

    def __getitem__(self, index):
        return self.as_tuple()[index]


class AlternateKeysDescriptor(object):

    def __get__(self, instance, cls):
        alternate_keys = []
        for constraint in cls.__table__.constraints:
            if not isinstance(constraint, UniqueConstraint):
                continue
            alternate_keys.append(
                InstanceAlternateKey(instance, constraint) if instance\
                else AlternateKey(cls, constraint)
            )
        return alternate_keys
