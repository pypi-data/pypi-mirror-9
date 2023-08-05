"""
Find file using an arbitrary list of search paths. Inspired by
Jinja's template loader classes.
"""
from os.path import abspath, join, dirname, exists
import os
import itertools
import types
import importlib

import six

from libtng.exceptions import ResourceDoesNotExist,\
    NOTIMPLEMENTED_SUBCLASS


__all__ = [
    'Finder',
    'FileSystemLoader',
    'ModuleLoader'
]


class FileNotFound(ResourceDoesNotExist):

    def __init__(self, tried):
        self.tried = tried

    def __str__(self):
        return str(self.tried)



def split_playbook_path(playbook):
    """
    Split a path into segments and perform a sanity check.  If it detects
    '..' in the path it will raise a `TemplateNotFound` error.
    """
    pieces = []
    sep = os.path.sep
    altsep = os.path.altsep
    for piece in playbook.split('/'):
        if sep in piece \
           or (altsep and altsep in piece) or \
           piece == os.pardir:
            raise playbook.PlaybookDoesNotExist(playbook)
        elif piece and piece != '.':
            pieces.append(piece)
    return pieces


class Finder(object):
    """
    The main filefinder class.
    """
    entity_class = unicode

    @property
    def loaders(self):
        if not self._loaders:
            loaders = []
            for loader in self.loader_classes:
                if isinstance(loader, BaseLoader):
                    loaders.append(loader)
                    continue
                module_name, class_name = loader.rsplit('.', 1)
                module = importlib.import_module(module_name)
                loader = getattr(module, class_name)()
                loaders.append(loader)
            self._loaders = loaders
        return self._loaders

    def __init__(self, loader_classes=None):
        self.loader_classes = loader_classes or []
        self._loaders = []

    def add_search_path(self, dirname):
        """
        Adds a new search path to the :class:`Finder`.

        :param dirname:
            a string specifying the search directory.
        """
        self._loader.append(FileSystemLoader([dirname]))

    def get_entity_instance(self, filepath, *args, **kwargs):
        return self.entity_class(filepath)

    def get(self, names, extra_loaders=None):
        """
        Get the absolute path to the first match in `names`.
        """
        tried = []
        if isinstance(names, six.string_types):
            names = [names]
        entity = None
        loaders = itertools.chain(self.loaders, extra_loaders or [])
        for entity_name, loader in itertools.product(names, loaders):
            try:
                src, uptodate = loader.get_source(self, entity_name)
                entity = self.get_entity_instance(src, uptodate)
            except FileNotFound as e:
                tried.extend(e.tried)
                continue
        if entity is None:
            raise FileNotFound(tried)
        return entity


Environment = Finder


#: A :class:`Finder` instance.
finder = Finder()


class BaseLoader(object):
    """
    Baseclass for all loaders.  Subclass this and override `get_source` to
    implement a custom loading mechanism.  The environment provides a
    `get_playbook` method that calls the loader's `load` method to get the
    filepath.
    """
    encoding='utf-8'

    @property
    def searchpath(self):
        return self._searchpath

    def __init__(self, searchpath=None):
        self._searchpath = searchpath

    def get_source(self, env, playbook):
        """
        Get the absolute filename for a file. It's passed the environment
        and name and has to return a tuple in the form ``(filename, uptodate)``
        and raise :exc:`playbook.FileNotFound` error if it can't locate
        the file.
        """
        raise NOTIMPLEMENTED_SUBCLASS

    def load(self, environment, name, globals=None):
        """Loads a playbook.  This method looks up the playbook in the cache
        or loads one by calling :meth:`get_source`.  Subclasses should not
        override this method as loaders working on collections of other
        loaders (such as :class:`PrefixLoader` or :class:`ChoiceLoader`)
        will not call this method but :attr:`BaseLoader.get_source`
        directly.
        """
        code = None
        if globals is None:
            globals = {}

        # first we try to get the source for this playbook together
        # with the filename.
        filename, uptodate = self.get_source(environment, name)
        return environment.playbook_class.fromfilepath(environment,
            filename, uptodate, globals=globals)

    def get_playbook_contents(self, src):
        return open_if_exists(src)


class FileSystemLoader(BaseLoader):
    """
    A :class:`BaseLoader` implementation that searches a file along
    an arbitrary list of search paths.
    """
    default_search_path = None

    def get_source(self, environment, name):
        pieces = split_playbook_path(name)
        tried = []
        for searchpath in self.searchpath:
            filename = join(searchpath, *pieces)
            if not exists(filename):
                tried.append(filename)
                continue
            return filename, True
        raise FileNotFound(tried)

    def __init__(self, searchpath=None):
        searchpath = searchpath or self.default_search_path or ''
        if isinstance(searchpath, six.string_types):
            searchpath = [searchpath]
        self._searchpath = searchpath


class ModuleLoader(FileSystemLoader):
    """
    A :class:`BaseLoader` implementation that searches in the package
    directories of an arbitrary module list. The modules must be
    importable.
    """

    #: Folders relative to the module directory to be added to
    #: the search path.
    folders = ['']

    @property
    def searchpath(self):
        if not self._searchpath:
            searchpath = []
            for module_name in self.modules:
                module = importlib.import_module(module_name)\
                    if not isinstance(module_name, types.ModuleType)\
                    else module_name
                basedir = dirname(module.__file__)
                searchpath.extend([join(basedir, x) for x in self.folders])
            self._searchpath = searchpath
        return self._searchpath

    def __init__(self, modules, folders=[''], *args, **kwargs):
        self.folders = folders
        self.modules = modules
        self._searchpath = []