#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module implements a transaction manager that can be used to define
transaction handling in a request or view function. It is used by transaction
control middleware and decorators.

The transaction manager can be in managed or in auto state. Auto state means the
system is using a commit-on-save strategy (actually it's more like
commit-on-change). As soon as the .save() or .delete() (or related) methods are
called, a commit is made.

Managed transactions don't do those commits, but will need some kind of manual
or implicit commits or rollbacks.
"""
from functools import wraps
from threading import local
import warnings

from sqlalchemy import func
from sqlalchemy.orm.session import PREPARED

from libtng import environ
from libtng import timezone
from libtng.const import DEFAULT_DB_ALIAS
from libtng.exceptions import ProgrammingError
from libtng.db.connection import connections


data = local()


class TransactionManagementError(ProgrammingError):
    """
    This exception is thrown when transaction management is used improperly.
    """
    pass

#################################
# Decorators / context managers #
#################################
class Atomic(object):
    """
    This class guarantees the atomic execution of a given block.

    An instance can be used either as a decorator or as a context manager.

    When it's used as a decorator, __call__ wraps the execution of the
    decorated function in the instance itself, used as a context manager.

    When it's used as a context manager, __enter__ creates a transaction or a
    savepoint, depending on whether a transaction is already in progress, and
    __exit__ commits the transaction or releases the savepoint on normal exit,
    and rolls back the transaction or to the savepoint on exceptions.

    It's possible to disable the creation of savepoints if the goal is to
    ensure that some code runs within a transaction without creating overhead.

    A stack of savepoints identifiers is maintained as an attribute of the
    connection. None denotes the absence of a savepoint.

    This allows reentrancy even if the same AtomicWrapper is reused. For
    example, it's possible to define `oa = @atomic('other')` and use `@oa` or
    `with oa:` multiple times.

    Since database connections are thread-local, this is thread-safe.
    """

    def __init__(self, using, savepoint=None, transaction_timestamp=None,
        session=None):
        assert (bool(using) ^ (session is not None))
        self.using = using
        self.session = session or connections.get_session(self.using)
        self.savepoint = savepoint
        self.transaction_timestamp = transaction_timestamp

    def is_nested(self):
        return self.session.transaction is not None

    def __enter__(self):
        connection = self.session
        is_nested = connection.transaction is not None
        connection.needs_rollback = False
        if connection.transaction and (connection.transaction._state == PREPARED):
            connection.transaction.rollback()
        self.transaction = connection.begin(nested=is_nested)

    def __exit__(self, exc_type, exc_value, traceback):
        connection = self.session
        if connection.needs_rollback:
            self.session.rollback()
            return
        if exc_type is None:
            try:
                self.session.commit()
            except Exception:
                self.session.rollback()
                raise
        else:
            self.session.rollback()



def atomic(using=None, savepoint=True, session=None):
    return Atomic(using, savepoint, session=session)



class SessionAuthorization(Atomic):

    def __init__(self, user_id, client_id, *args, **kwargs):
        self.user_id = user_id
        self.client_id = client_id
        Atomic.__init__(self, *args, **kwargs)

    def __enter__(self):
        session = self.session

        self.invoking_user_id = session.execute(func.get_session_user())\
            .scalar()
        self.invoking_client_id = session.execute(func.get_session_client())\
            .scalar()
        Atomic.__enter__(self)
        session.execute(func.set_session_user(self.user_id))
        session.execute(func.set_session_client(self.client_id))

    def __exit__(self, exc_type, exc_value, traceback):
        Atomic.__exit__(self, exc_type, exc_value, traceback)
        session = self.session
        if exc_type is None:
            session.execute(func.set_session_user(self.invoking_user_id))
            session.execute(func.set_session_client(self.invoking_client_id))



def session_authorization(user_id, client_id, using=None, savepoint=True, session=None):
    return SessionAuthorization(user_id, client_id,
        using=using, session=session, savepoint=savepoint)
