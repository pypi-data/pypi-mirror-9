import json
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.utils.translation import get_language
from djinn_core.views.admin import AdminMixin
from djinn_i18n.tool import TOOL


class TransView(TemplateView, AdminMixin):

    def get_template_names(self):

        if self.request.is_ajax():
            return "djinn_i18n/modaltrans.html"
        else:
            return "djinn_i18n/trans.html"

    @property
    def msgid(self):

        return self.request.REQUEST.get('msgid')

    @property
    def locale(self):

        return self.kwargs.get('locale') or get_language()

    def get(self, request, *args, **kwargs):

        self.entry = TOOL.get_entry(self.msgid, self.locale)

        return super(TransView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):

        TOOL.translate(self.msgid, request.POST.get('msgstr'), self.locale)

        if self.request.is_ajax():
            return HttpResponse(json.dumps({'status': 'ok'}, skipkeys=True))
        else:
            return HttpResponseRedirect(reverse("djinn_i18n_index"))
