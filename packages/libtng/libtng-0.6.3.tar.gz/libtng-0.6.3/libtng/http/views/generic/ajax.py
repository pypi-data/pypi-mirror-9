from libtng.http.exceptions import Forbidden
from libtng.http.views.generic.base import View


class AjaxView(View):

    def dispatch(self, request, *args, **kwargs):
        if not request.is_ajax():
            f = getattr(self, 'render_to_response',
                self.response_factory)
            raise Forbidden(hint="This URI is only available to Ajax requests.",
                detail="'X-Requested-With' header was missing or did not specify 'XMLHttpRequest'.",
                mimetype=self.mimetype, response_factory=f)
        return super(AjaxView, self).dispatch(request, *args, **kwargs)