from django.template import loader, Context, RequestContext # TODO: Remove

from libtng.template.response.base import BaseTemplateResponse


class TemplateResponse(BaseTemplateResponse):

    def __init__(self, request, template, context=None, content_type=None,
            status=None, current_app=None):
        # self.request gets over-written by django.test.client.Client - and
        # unlike context_data and template_name the _request should not
        # be considered part of the public API.
        self._request = request
        # As a convenience we'll allow callers to provide current_app without
        # having to avoid needing to create the RequestContext directly
        self._current_app = current_app
        super(TemplateResponse, self).__init__(
            template, context, content_type, status)

    def resolve_context(self, context):
        """Convert context data into a full RequestContext object
        (assuming it isn't already a Context object).
        """
        if isinstance(context, Context):
            return context
        return RequestContext(self._request, context)