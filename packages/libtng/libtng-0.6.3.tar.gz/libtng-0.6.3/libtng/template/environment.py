from jinja2 import Environment
from jinja2 import Template
from jinja2 import FileSystemLoader

from libtng import six
from libtng.template.template import Template
from libtng.module_loading import import_string
from libtng import safestring
import libtng.translation


JINJA2_ENVIRONMENT_OPTIONS          = {}
JINJA2_EXTENSIONS                   = {}
JINJA2_FILTERS                      = {}
JINJA2_FILTERS_REPLACE_FROM_DJANGO  = False
JINJA2_TESTS                        = {}
JINJA2_GLOBALS                      = {}
JINJA2_AUTOESCAPE                   = True
JINJA2_NEWSTYLE_GETTEXT             = True
JINJA2_CONSTANTS                    = {}
JINJA2_BYTECODE_CACHE_ENABLE        = False
JINJA2_BYTECODE_CACHE_NAME          = 'default'
JINJA2_BYTECODE_CACHE_BACKEND       = None
DEFAULT_EXTENSIONS = [
    "jinja2.ext.do",
    "jinja2.ext.loopcontrols",
    "jinja2.ext.with_",
    "jinja2.ext.i18n",
    "jinja2.ext.autoescape",
]


class Environment(Environment):

    def configure(self, **opts):
        if not hasattr(self, 'conf'):
            self.conf = {}
        self.conf.update(opts)

    def initialize(self):
        self.initialize_i18n()
        self.initialize_bytecode_cache()
        self.initialize_template_loader()
        self.initialize_autoescape()
        self.initialize_builtins()

    def initialize_i18n(self):
        # install translations
        if self.conf.get('use_i18n'):
            self.install_gettext_translations(libtng.translation,
                newstyle=JINJA2_NEWSTYLE_GETTEXT)
        else:
            self.install_null_translations(newstyle=JINJA2_NEWSTYLE_GETTEXT)

    def initialize_bytecode_cache(self):
        # Install bytecode cache if is enabled
        if JINJA2_BYTECODE_CACHE_ENABLE:
            cls = utils.load_class(JINJA2_BYTECODE_CACHE_BACKEND)
            self.bytecode_cache = cls(JINJA2_BYTECODE_CACHE_NAME)

    def initialize_template_loader(self):
        self.template_class = self.conf.get('template_class', Template)
        self.loader = FileSystemLoader(self.conf.get('template_dirs', []))

    def initialize_autoescape(self):
        if not self.autoescape:
            return
        if hasattr(safestring, "SafeText"):
            if not hasattr(safestring.SafeText, "__html__"):
                safestring.SafeText.__html__ = lambda self: six.text_type(self)
        if hasattr(safestring, "SafeString"):
            if not hasattr(safestring.SafeString, "__html__"):
                safestring.SafeString.__html__ = lambda self: six.text_type(self)
        if hasattr(safestring, "SafeUnicode"):
            if not hasattr(safestring.SafeUnicode, "__html__"):
                safestring.SafeUnicode.__html__ = lambda self: six.text_type(self)
        if hasattr(safestring, "SafeBytes"):
            if not hasattr(safestring.SafeBytes, "__html__"):
                safestring.SafeBytes.__html__ = lambda self: six.text_type(self)

    def initialize_builtins(self):
        for name, value in self.conf.get('jinja2_filters', {}).items():
            if isinstance(value, six.string_types):
                self.filters[name] = import_string(value)
            else:
                self.filters[name] = value
        for name, value in self.conf.get('jinja2_globals', {}).items():
            if isinstance(value, six.string_types):
                self.globals[name] = import_string(value)
            else:
                self.globals[name] = value



