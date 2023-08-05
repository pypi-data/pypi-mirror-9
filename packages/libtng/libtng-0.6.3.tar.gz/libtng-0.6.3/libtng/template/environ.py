import jinja2
import jinja2.exceptions

from libtng.template.environment import Environment
from libtng.template.environment import JINJA2_AUTOESCAPE
from libtng.template.environment import JINJA2_EXTENSIONS
from libtng.template.environment import DEFAULT_EXTENSIONS

from libtng.template.exceptions import TemplateDoesNotExist


initial_params = {
    'autoescape'    : False,
    'extensions'    : list(set(list(JINJA2_EXTENSIONS) + DEFAULT_EXTENSIONS)),
    'trim_blocks'   : True,
    'lstrip_blocks' : True
}
environment = Environment(
    undefined=jinja2.StrictUndefined,
    **initial_params
)
environment.configure(
    use_i18n=True,
    template_dirs=[]
)


def configure(**opts):
    """Configures the :mod:`jinja2` environment with the specified
    *opts*.
    """
    return environment.configure(**opts)


def initialize():
    """Initializes the environment. Must always be called after
    :func:`configure`.
    """
    environment.initialize()


def get_template(template_name):
    """Lookup a :class:`~libtng.template.Template` instance
    identifier by it's `template_name`.
    """
    try:
        return environment.get_template(template_name)
    except jinja2.exceptions.TemplateNotFound:
        raise TemplateDoesNotExist(template_name)
