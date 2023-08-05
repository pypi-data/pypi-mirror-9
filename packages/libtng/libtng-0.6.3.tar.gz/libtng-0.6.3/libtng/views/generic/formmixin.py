import abc

from libtng.encoding import force_text
from libtng.http import Redirect
from libtng.exceptions import ProgrammingError
from libtng.views.generic.base import ContextMixin


class FormMixin(ContextMixin):
    """
    A mixin that provides a way to show and handle a form in a request.
    """
    initial = {}
    prefix = None
    redirect_class = Redirect

    @abc.abstractproperty
    def form_class(self):
        raise NotImplementedError

    @abc.abstractproperty
    def success_url(self):
        raise NotImplementedError

    def get_initial(self):
        """
        Returns the initial data to use for forms on this view.
        """
        return self.initial.copy()

    def get_prefix(self):
        """
        Returns the prefix to use for forms on this view
        """
        return self.prefix

    def get_form_class(self):
        """
        Returns the form class to use in this view
        """
        return self.form_class

    def get_form(self, form_class):
        """
        Returns an instance of the form to be used in this view.
        """
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {
            'initial': self.get_initial(),
            'prefix': self.get_prefix(),
        }

        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.form,
                'files': self.request.files,
            })
        return kwargs

    def get_success_url(self):
        """
        Returns the supplied success URL.
        """
        if self.success_url:
            # Forcing possible reverse_lazy evaluation
            url = force_text(self.success_url)
        else:
            raise ProgrammingError(
                "No URL to redirect to. Provide a success_url.")
        return url

    def form_valid(self, form):
        """
        If the form is valid, redirect to the supplied URL.
        """
        return self.get_redirect_response()

    def form_invalid(self, form):
        """
        If the form is invalid, re-render the context data with the
        data-filled form and errors.
        """
        return self.render_to_response(self.get_context_data(form=form))

    def get_redirect_response(self):
        """
        Returns a response that redirects to the form success page.
        """
        return self.redirect_class(self.get_success_url())