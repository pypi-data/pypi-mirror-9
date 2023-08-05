import importlib

from libtng.ioc.provider import _provider
from libtng.ioc.dependency import Dependency


provide = _provider.provide
require = lambda *args, **kwargs: Dependency(*args, **kwargs)


def ensure_modules_loaded(modules):
    """
    Ensure that the specified modules are loaded into the
    interpreter memory.
    """
    map(importlib.import_module, modules)