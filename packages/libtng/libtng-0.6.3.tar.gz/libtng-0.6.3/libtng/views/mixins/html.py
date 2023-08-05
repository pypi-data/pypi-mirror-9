import copy

from libtng.translation import ugettext_lazy as _


class HtmlViewMixin(object):
    page_title = _('Nameless')
    default_context = {}

    def get_context_data(self, *args, **kwargs):
        context_data = super(HtmlViewMixin, self).get_context_data(*args, **kwargs)
        context_data.update({
            'page_title': self.get_page_title(self.request)
        })
        context_data.update(copy.deepcopy(self.default_context or {}))
        return context_data

    def get_page_title(self, request):
        return self.page_title