import functools
import json
import importlib

from libtng import six
from libtng.http.rest.exceptions import ProjectorDoesNotExist


YAML_MIMETYPES = ['application/yaml','application/x-yaml','text/yaml','text/x-yaml']


class Formatter(object):

    @property
    def mimetypes(self):
        return [self.mimetype] if isinstance(self.mimetype, six.string_types)\
            else self.mimetype

    def __init__(self, mimetype, func, args, kwargs):
        self.mimetype = mimetype
        self.func = func
        self.args = args
        self.kwargs = kwargs


def formatter(mimetype, *args, **kwargs):
    """
    Used on instance methods of a :class:`Projector` subclass
    to indicate the method is used to project the specified
    content type.
    """
    def decorator(func):
        return Formatter(mimetype, func, args, kwargs)
    return decorator


class ProjectorMeta(type):

    def __new__(cls, name, bases, attrs):
        attrs['_formatters'] = {}
        for attr, value in attrs.items():
            if not isinstance(value, Formatter):
                continue
            for mimetype in value.mimetypes:
                attrs['_formatters'][mimetype] = value.func, \
                    value.args, value.kwargs
            attrs[attr] = value.func
        return super(ProjectorMeta, cls).__new__(cls, name, bases, attrs)



class Projector(six.with_metaclass(ProjectorMeta)):

    @property
    def mimetypes(self):
        return tuple(sorted(self._formatters.keys()))

    def project(self, mimetype, serialized):
        """
        Project to content to the desired mimetype.
        """
        try:
            f, args, kwargs = self._formatters[mimetype]
        except KeyError:
            raise ProjectorDoesNotExist(mimetype)
        else:
            return f(self, serialized, *args, **kwargs)

    def can_project(self, mimetype):
        """
        Return a :class:`bool` indicating if the projector can
        project the specified `mimetype`.
        """
        return mimetype in self._formatters

    @formatter('application/json', indent=4)
    def as_json(self, serialized, *args, **kwargs):
        """
        Format the serialized data as JavaScript Object Notation (JSON).

        Args:
            serialized (dict): the serialized data.

        Returns:
            str, dict
        """
        content = json.dumps(serialized, *args, **kwargs)
        return content, {}

    @formatter(YAML_MIMETYPES, default_flow_style=False, indent=4)
    def as_yaml(self, serialized, *args, **kwargs):
        """
        Format the serialized data as Yet Another Markup Language (YAML).

        Args:
            serialized (dict): the serialized data.

        Returns:
            str, dict
        """
        content = importlib.import_module('yaml')\
            .safe_dump(serialized, *args, **kwargs)
        return content, {}