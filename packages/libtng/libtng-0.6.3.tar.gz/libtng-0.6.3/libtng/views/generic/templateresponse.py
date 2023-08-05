from importlib import import_module
import abc

from libtng import six
from libtng.functional import SimpleLazyObject
from libtng.exceptions import ProgrammingError


TemplateResponse = SimpleLazyObject(lambda: import_module('libtng.template.response.TemplateResponse'))


class TemplateResponseMixin(six.with_metaclass(abc.ABCMeta)):
    """
    A mixin that can be used to render a template.
    """
    response_class = None

    @abc.abstractproperty
    def template_name(self):
        """A string specifying the name of the template to render."""
        raise NotImplementedError

    @abc.abstractproperty
    def content_type(self):
        """A string indicating the mimetype of the response."""
        raise NotImplementedError

    @property
    def mimetype(self):
        """Alias for `content_type`."""
        return self.content_type

    def render_to_response(self, context, **response_kwargs):
        """
        Returns a response, using the `response_class` for this
        view, with a template rendered with the given context.

        If any keyword arguments are provided, they will be
        passed to the constructor of the response class.
        """
        response_kwargs.setdefault('content_type', self.content_type)
        return self.get_response(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            **response_kwargs
        )

    def get_template_names(self):
        """
        Returns a list of template names to be used for the request. Must return
        a list. May not be called if render_to_response is overridden.
        """
        if self.template_name is None:
            raise ProgrammingError(
                "TemplateResponseMixin requires either a definition of "
                "'template_name' or an implementation of 'get_template_names()'")
        else:
            return [self.template_name]

    def get_response(self, *args, **kwargs):
        if self.response_class is None:
            raise ProgrammingError("View should define a `response_class`.")
        return self.response_class(*args, **kwargs)