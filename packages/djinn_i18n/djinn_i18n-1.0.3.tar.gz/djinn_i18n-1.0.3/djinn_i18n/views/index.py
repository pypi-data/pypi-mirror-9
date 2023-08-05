from django.views.generic import TemplateView
from django.conf import settings
from djinn_core.views.admin import AdminMixin
from djinn_i18n.tool import TOOL
from djinn_i18n.utils import clear_trans_cache


class IndexView(TemplateView, AdminMixin):

    template_name = "djinn_i18n/index.html"

    @property
    def default_language(self):

        return settings.LANGUAGE_CODE

    def list_languages(self):

        return settings.LANGUAGES

    def list_modules(self):

        """ List po files modules """

        return TOOL.list_modules().keys()

    @property
    def tainted(self):

        return TOOL.tainted


class SaveView(IndexView):

    def get(self, request, *args, **kwargs):

        TOOL.save(mo=True)

        clear_trans_cache()

        return super(SaveView, self).get(request, *args, **kwargs)


class SearchView(TemplateView, AdminMixin):

    template_name = "djinn_i18n/search.html"

    @property
    def locale(self):

        return self.request.GET.get('locale')

    def list_languages(self):

        return settings.LANGUAGES

    def list_entries(self):

        return TOOL.find_entries(self.request.GET.get('q'), self.locale)
