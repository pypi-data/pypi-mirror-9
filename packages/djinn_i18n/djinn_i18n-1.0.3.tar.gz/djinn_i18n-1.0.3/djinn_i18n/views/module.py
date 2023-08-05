from django.views.generic import TemplateView
from djinn_i18n.tool import TOOL
from djinn_core.views.admin import AdminMixin


class ModuleView(TemplateView, AdminMixin):

    template_name = "djinn_i18n/module.html"

    @property
    def module(self):

        return self.kwargs.get('module')

    @property
    def locale(self):

        return self.kwargs.get('locale')

    def list_entries(self):

        return TOOL.list_entries(self.module, self.locale)
