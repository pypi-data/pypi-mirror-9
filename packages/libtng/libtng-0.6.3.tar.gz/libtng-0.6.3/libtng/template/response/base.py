from django.template import loader, Context, RequestContext # TODO: Remove
from django.template.response import SimpleTemplateResponse

from libtng.template import loader
from libtng import six


class BaseTemplateResponse(SimpleTemplateResponse):

    def resolve_template(self, template):
        "Accepts a template object, path-to-template or list of paths"
        if isinstance(template, (list, tuple)):
            t = loader.select_template(template)
        elif isinstance(template, six.string_types):
            t = loader.get_template(template)
        else:
            t = template
        return t

