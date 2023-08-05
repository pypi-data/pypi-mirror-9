import itertools
import os

from libtng import six
from libtng.template import environ
from libtng.template.exceptions import TemplateDoesNotExist


def select_template(template_list, dirs=None):
    """
    Return a :class:`~libtng.Template` instance representing the
    first match in the specified `template_list`.
    """
    template, origin = find_template(template_list, dirs)
    if not hasattr(template, 'render'):
        # template needs to be compiled
        template = get_template_from_string(template, origin, template_name)
    return template


def get_template(template_name_list, dirs=None):
    """
    Return a :class:`~libtng.Template` instance representing the
    template specified by `template_name`.
    """
    if not template_name_list:
        raise TemplateDoesNotExist("No template names provided")
    not_found = []
    for template_name in template_name_list:
        try:
            return environ.get_template(template_name)
        except TemplateDoesNotExist as e:
            if e.args[0] not in not_found:
                not_found.append(e.args[0])
            continue
    # If we get here, none of the templates could be loaded
    raise TemplateDoesNotExist(', '.join(not_found))


def get_template_from_string(source, origin=None, name=None):
    """
    Returns a compiled Template object for the given template code,
    handling template inheritance recursively.
    """
    return Template(source, origin, name)


def find_template(name, dirs=None):
    if isinstance(name, six.string_types):
        name = [name]
    tried = []
    for basedir, template_name in itertools.product(dirs or [''], name):
        src = os.path.join(basedir, template_name)
        try:
            template = environ.get_template(src)
        except TemplateDoesNotExist:
            continue
        return template, None
        tried.append(template_name)
    raise TemplateDoesNotExist(tried)