from libtng.views.generic.formmixin import FormMixin
from libtng.views.generic.processform import ProcessFormView


class BaseFormView(FormMixin, ProcessFormView):
    """
    A base view for displaying a form
    """