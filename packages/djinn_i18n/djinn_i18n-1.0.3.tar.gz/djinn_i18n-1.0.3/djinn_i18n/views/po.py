import json
import polib
from django.views.generic import View
from django.http import HttpResponse
from djinn_i18n.tool import TOOL


class EntryEncoder(json.JSONEncoder):

    def default(self, obj):

        if isinstance(obj, polib.POEntry):
            return {'msgid': obj.msgid,
                    'msgstr': obj.msgstr,
                    'comment': obj.comment,
                    'tcomment': obj.tcomment}

        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)


class POView(View):

    @property
    def locale(self):

        return self.kwargs.get('locale')

    def get(self, request, *args, **kwargs):

        entries = TOOL.get_entries(self.locale)

        return HttpResponse(json.dumps(entries, skipkeys=True,
                                       cls=EntryEncoder),
                            content_type="application/json")
