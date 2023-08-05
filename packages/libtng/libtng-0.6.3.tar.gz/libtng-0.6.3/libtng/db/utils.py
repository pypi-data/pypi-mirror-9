import importlib

from libtng import six
from libtng.const import DEFAULT_DB_ALIAS
from libtng import environ

__all__ = [
    'router'
]


class ConnectionRouter(object):
    """
    Routes CRUD operations to their appropriate database connections.
    """

    def __init__(self, routers=None):
        self.__routers = routers or []

    @property
    def routers(self):
        routers = []
        for r in (self.__routers or []):
            if isinstance(r, six.string_types):
                router = importlib.import_module(r)()
            else:
                router = r
            routers.append(router)
        return routers

    def set_routers(self, routers):
        """
        Set routers to use.

        :param routers:
            a list of string pointing to the module-qualified
            names of connection router classes.
        """
        self.__routers = routers

    def _router_func(action):
        def _route_db(self, model, **hints):
            chosen_db = None
            for router in self.routers:
                try:
                    method = getattr(router, action)
                except AttributeError:
                    # If the router doesn't have a method, skip to the next one.
                    pass
                else:
                    chosen_db = method(model, **hints)
                    if chosen_db:
                        return chosen_db
            try:
                return hints['instance']._state.db or environ.getenv('DEFAULT_DB_ALIAS', DEFAULT_DB_ALIAS)
            except KeyError:
                return environ.getenv('DEFAULT_DB_ALIAS', DEFAULT_DB_ALIAS)
        return _route_db

    db_for_read = _router_func('db_for_read')
    db_for_write = _router_func('db_for_write')

    def allow_relation(self, obj1, obj2, **hints):
        for router in self.routers:
            try:
                method = router.allow_relation
            except AttributeError:
                # If the router doesn't have a method, skip to the next one.
                pass
            else:
                allow = method(obj1, obj2, **hints)
                if allow is not None:
                    return allow
        return obj1._state.db == obj2._state.db

    def allow_syncdb(self, db, model):
        for router in self.routers:
            try:
                method = router.allow_syncdb
            except AttributeError:
                # If the router doesn't have a method, skip to the next one.
                pass
            else:
                allow = method(db, model)
                if allow is not None:
                    return allow
        return True


router = ConnectionRouter()