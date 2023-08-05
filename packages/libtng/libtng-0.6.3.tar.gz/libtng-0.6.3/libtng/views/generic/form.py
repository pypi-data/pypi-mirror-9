from libtng.views.generic.templateresponse import TemplateResponseMixin
from libtng.views.generic.baseform import BaseFormView


class FormView(TemplateResponseMixin, BaseFormView):
    """
    A view for displaying a form, and rendering a template response.
    """