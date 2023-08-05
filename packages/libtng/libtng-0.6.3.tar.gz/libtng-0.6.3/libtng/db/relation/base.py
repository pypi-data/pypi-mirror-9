from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.declarative.api import _declarative_constructor
from sqlalchemy.ext.declarative.api import DeclarativeMeta
from sqlalchemy.ext.declarative.api import _as_declarative
from sqlalchemy.orm import mapper as _mapper
from sqlalchemy.orm.exc import NoResultFound
from sqlalchemy import MetaData
import sqlalchemy as sa

from libtng.db.relation.pk import PrimaryKeyDescriptor
from libtng.db.relation.ak import AlternateKeysDescriptor


RESERVED_ATTRS = set(['_pk','_alternatekeys'])


class NoValidIdentifier(Exception):
    pass


class IdentifiersDescriptor(object):

    def __get__(self, instance, cls):
        return ([cls._pk] + cls._alternatekeys) if not instance\
            else ([instance._pk] + instance._alternatekeys)


class RelationMetaclass(DeclarativeMeta):
    """
    Metaclass used to construct a :class:`Relation` subclass.
    """

    # def __init__(cls, classname, bases, dict_):
    #     if '_decl_class_registry' not in cls.__dict__:
    #         _as_declarative(cls, classname, cls.__dict__)
    #     type.__init__(cls, classname, bases, dict_)

    def __new__(cls, name, bases, attrs):
        super_new = super(RelationMetaclass, cls).__new__

        if set(attrs.keys()) & RESERVED_ATTRS:
            raise TypeError("Reserved attribute clash: {0}".format(RESERVED_ATTRS))

        # attrs will never be empty for classes declared in the standard way
        # (ie. with the `class` keyword). This is quite robust.
        if name == 'Relation':
            return super_new(cls, name, bases, attrs)

        # Also ensure initialization is only performed for subclasses of Model
        # (excluding Model class itself).
        parents = [b for b in bases if isinstance(b, RelationMetaclass) and
                not (b.__name__ == 'Relation' and b.__mro__ == (b, object))]
        if not parents:
            return super_new(cls, name, bases, attrs)

        # Add the primary key descriptor
        attrs['_pk'] = PrimaryKeyDescriptor()
        attrs['_alternatekeys'] = AlternateKeysDescriptor()
        attrs['_identifiers'] = IdentifiersDescriptor()
        attrs['DoesNotExist'] = type('DoesNotExist', (NoResultFound,), {})
        return super_new(cls, name, bases, attrs)

    def add_to_class(cls, name, value):
        if hasattr(value, 'contribute_to_class'):
            value.contribute_to_class(cls, name)
        else:
            setattr(cls, name, value)


class BaseRelation(object):

    def refresh_pk(self, session):
        """
        Refresh the object state against the current state in
        the persistant storage. Raises :exc:`NoValidIdentifier`
        if the object can not be identified.
        """
        ident = self.get_valid_identifier()
        dbo = ident.get_object(session)
        dbo._pk.set_identifying_attributes(self)

    def has_valid_pk(self):
        """
        Return a boolean indicating if the object has specified
        a valid primary key.
        """
        return self._pk.is_valid()

    def get_valid_identifier(self):
        """
        Return the first matching valid identifier.
        """
        for identifier in self._identifiers:
            if identifier.is_valid():
                return identifier
        raise NoValidIdentifier("Unable to find a key for identification.")

    def get_primary_key(self, setter=lambda **k: None):
        """
        Returns the primary key of the entity represented as a
        :class:`~libtng.db.relation.InstancePrimaryKey` instance.
        The caller may optionally specify a `setter`, which is
        a callable. The provided `setter` will be called with the
        primary key as it's keyword arguments.
        """
        pk = self._pk
        setter(**pk.as_dict())
        return pk


    def is_persistent(self, session):
        """
        Guess if the object is persistent by finding the first
        valid identifier (key) and quering the database for
        existence. :meth:`is_persistent` will return ``True``
        if any of the keys is found.
        """
        persistent = False
        q = session.query(type(self))
        predicate = []
        for identifier in self._identifiers:
            if not identifier.is_valid():
                continue
            predicate.append(identifier.predicate())
        return session.query(q.filter(sa.or_(*predicate)).exists()).scalar()\
            if predicate else False

    def persist(self, session=None):
        created = False
        updated = False
        if not self.is_persistent(session):
            session.add(self)
            created = True
        else:
            self.refresh_pk(session)
            session.merge(self)
            updated = True
        session.flush()
        assert created ^ updated
        return created

    def as_dict(self, columns=None):
        values = {}
        only = columns or []
        for column in self.__table__.columns:
            if column.name not in only:
                continue
            values[column.name] = str(getattr(self, column.name))
        return values


def constructor(self, *args, **kwargs):
    _declarative_constructor(self, *args, **kwargs)



def mapper(cls, table=None, *arg, **kw):
    """
    Class mapper that adds the subclasses of :class:`Relation` to the
    :mod:`tngems` class registry.
    """
    return _mapper(cls, table, *arg, **kw)


Relation = declarative_base(
    cls = BaseRelation,
    metaclass = RelationMetaclass,
    constructor = constructor,
    mapper = mapper,
    metadata=MetaData()
)


def relation_factory():
    return declarative_base(
        cls = BaseRelation,
        metaclass = RelationMetaclass,
        constructor = constructor,
        mapper = mapper,
        metadata=MetaData()
    )
