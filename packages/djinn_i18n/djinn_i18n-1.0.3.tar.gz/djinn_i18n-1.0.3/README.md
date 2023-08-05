djinn_i18n
==========

Djinn i18n module providing overrides of djinn translations. Other
than for instance Rosetta, this tool writes it's overrides to a
separate .po file that resides outside of your or other people's
sources, so you won't get into trouble when updating source code.

The one single .po file is written to settings.PO\_OVERRIDES, or if
that doesn't exist, to: settings.PROJECT\_ROOT/var/locale.

Make sure to add the path to your settings.LOCALE\_PATHS, like so:

    LOCALE_PATHS = [PO_OVERRIDES] + LOCALE_PATHS

or:

    LOCALE_PATHS = [PROJECT_ROOT + "/var/locale"] + LOCALE_PATHS
