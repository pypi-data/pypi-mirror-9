import polib
from django.conf import settings
from djinn_i18n.po import load_po
from djinn_i18n.utils import get_translatable_apps


class TransTool(object):

    tainted = False

    def __init__(self):

        self.modules = self.list_modules()
        self.overrides = {}
        self.entries = {}
        self.module_entries = {}

        for locale, language in settings.LANGUAGES:

            self.overrides[locale] = load_po(locale)

        for locale, language in settings.LANGUAGES:

            self.entries[locale] = self._fill_entries(locale)

    def translate(self, msgid, msgstr, locale):

        self.tainted = True

        orig_entry = self.entries[locale][msgid]

        self.overrides[locale].update(
            msgid, msgstr,
            comment=orig_entry.comment,
            tcomment=orig_entry.tcomment
        )

        # update tool entry
        self.entries[locale][msgid].msgstr = msgstr

        self.save(mo=True)

    def save(self, mo=False):

        """ Save the override po files. If mo is true-ish, also compile """

        for po in self.overrides.values():

            po.save()

            if mo:

                po.save_mo()

        self.tainted = False

    def list_modules(self):

        """ List all locale modules and return a map of module, path """

        return get_translatable_apps()

    def list_entries(self, module, locale):

        return [self.entries[locale][msgid] for msgid in
                self.module_entries[module]]

    def _list_entries(self, module, locale):

        """List entries by actually reading the po files. Don't overdo
        this...
        """

        path = self.modules[module]

        pofile_path = "%s/%s/LC_MESSAGES/django.po" % (path, locale)

        try:
            pofile = polib.pofile(pofile_path)
            return [e for e in pofile if not e.obsolete]
        except:
            return []

    def _fill_entries(self, locale):

        _entries = {}

        for entry in self.overrides[locale]:
            _entries[entry.msgid] = entry

        for module in self.modules.keys():

            self.module_entries[module] = []

            for entry in self._list_entries(module, locale):

                self.module_entries[module].append(entry.msgid)

                if entry.msgid not in _entries.keys():
                    _entries[entry.msgid] = entry

        return _entries

    def find_entries(self, frag, locale):

        def _filter(entry):

            _text = "%s %s %s %s" % (entry.msgid, entry.msgstr,
                                     entry.comment, entry.tcomment)

            return frag.lower() in _text.lower()

        return filter(_filter, self.entries[locale].values())

    def is_override(self, entry, locale):

        return self.overrides[locale].has_entry(entry)

    def get_entry(self, msgid, locale):

        return self.entries[locale].get(msgid)

    def get_entries(self, locale):

        """ List all entries """

        return self.entries[locale]


TOOL = TransTool()
