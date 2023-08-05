import polib
import os
from utils import generate_po_path, get_override_base


def load_po(locale):

    """ Either load exisint po overrides, or create new one """

    path = generate_po_path(get_override_base(), locale)

    if not os.path.exists(path):

        if not os.path.exists(os.path.dirname(path)):

            os.makedirs(os.path.dirname(path))

        po = POFile()

        po.metadata = {
            'Project-Id-Version': '1.0',
            'Report-Msgid-Bugs-To': 'devnull@pythonunited.com',
            'POT-Creation-Date': '2007-10-18 14:00+0100',
            'PO-Revision-Date': '2007-10-18 14:00+0100',
            'Last-Translator': 'djinn <djinn@pythonunited.com',
            'Language-Team': ('%s <djinn@pythonunited.com>' % locale),
            'MIME-Version': '1.0',
            'Content-Type': 'text/plain; charset=utf-8',
            'Content-Transfer-Encoding': '8bit',
        }

        po.fpath = path

    else:
        po = polib.pofile(path, klass=POFile)

    return po


class POFile(polib.POFile):

    def __init__(self, *args, **kwargs):

        super(POFile, self).__init__(*args, **kwargs)

        self._msg_map = {}

        for entry in self:
            self._msg_map[entry.msgid] = entry

    def save_mo(self):

        mopath = "%s.mo" % os.path.splitext(self.fpath)[0]

        self.save_as_mofile(mopath)

    def update(self, msgid, msgstr, **kwargs):

        if msgid in self._msg_map.keys():
            self._msg_map[msgid].msgstr = msgstr
        else:
            entry = polib.POEntry(
                msgid=msgid,
                msgstr=msgstr,
                **kwargs
            )

            self.append(entry)

    def append(self, entry):

        """ Append and add to map """

        super(POFile, self).append(entry)

        self._msg_map[entry.msgid] = entry

    def has_entry(self, entry):

        return entry.msgid in self._msg_map.keys()
