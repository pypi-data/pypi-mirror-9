"""
:mod:`libtng` runtime settings configuration.
"""
import sys
import collections
try:
    import configparser
except ImportError:
    import ConfigParser as configparser

from libtng.module_loading import import_string
from libtng.const import DEFAULT_DB_ALIAS


class NOT_PROVIDED:
    pass


class Settings(object):


    @classmethod
    def fromfile(cls, *filenames):
        config = configparser.ConfigParser()
        config.read(filenames)
        return cls.fromconfig(config)

    @classmethod
    def setup_environ(cls, *filenames):
        settings = cls.fromfile(*filenames)
        settings.setup_interpreter()
        settings.setup_databases(import_string('libtng.db.connections'))
        return settings

    @classmethod
    def fromconfig(cls, config):
        """Create a new :class:`Settings` object using settings parsed
        by :mod:`configparser.ConfigParser`.

        Args:
            config (configparser.ConfigParser): the runtime configuration
                parsed from INI files on disk.

        Returns:
            Settings
        """
        settings = collections.defaultdict(dict)
        for section in config.sections():
            for key, value in config.items(section):
                settings[section][key] = value
        return cls(settings)

    def __init__(self, settings):
        self._raw_settings = settings
        self._configurables = []

    def get(self, section, name, default=NOT_PROVIDED, type=lambda x: x):
        """Return the value identified by section and name."""
        try:
            if type == bool:
                value = self._raw_settings[section][name]
                return value in ('yes', 'true','True')
            else:
                return type(self._raw_settings[section][name])
        except KeyError:
            if default == NOT_PROVIDED:
                raise
            return type(default)

    def setdefault(self, section, name, value):
        self._raw_settings[section].setdefault(name, value)

    def setup_interpreter(self):
        """Setup the Python interpreter."""
        interpeter = self._raw_settings.get('interpeter')
        if interpeter:
            if 'pythonpath' in interpeter:
                sys.path.extend(interpeter['pythonpath'].split(':'))


    def setup_databases(self, connections):
        """Setup the runtime configuration of database connections.

        Args:
            connections: an object responsible for registering database
                aliases/connections. It must specify an ``add`` method
                that takes the alias, and connection parameters as it's
                arguments e.g. ``connections.add(alias, dsn, **params)``.

        Returns:
            None
        """
        databases = {}
        for key, params in self._raw_settings.items():
            if not key.startswith('database'):
                continue
            alias = key.split(':')[-1] if ':' in key\
                else DEFAULT_DB_ALIAS
            dsn = params.pop('dsn')
            connections.add(alias, dsn, **params)

    def setup_brokers(self, brokers):
        """
        Setup asynchronous message queue brokers. Brokers are defined
        in a settings file as:

            [broker:<alias>]
            dsn = amqp://name:password@host/vhost

        Args:
            brokers: an object holding the brokers registry.
                Must specify an ``add`` method that takes the
                alias and dsn as it's arguments.

        Returns:
            None
        """
        for key, params in self._raw_settings.items():
            if not key.startswith('broker'):
                continue
            alias = key.split(':')[-1] if ':' in key\
                else DEFAULT_DB_ALIAS
            dsn = params.pop('dsn')
            brokers.add(alias, dsn, **params)

    def has_section(self, section):
        return section in self._raw_settings

    def has_option(self, section, name):
        return name in self._raw_settings.get(section, {})
