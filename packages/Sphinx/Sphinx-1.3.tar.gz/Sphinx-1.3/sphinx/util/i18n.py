# -*- coding: utf-8 -*-
"""
    sphinx.util.i18n
    ~~~~~~~~~~~~~~~~

    Builder superclass for all builders.

    :copyright: Copyright 2007-2015 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""

from os import path
from collections import namedtuple

from babel.messages.pofile import read_po
from babel.messages.mofile import write_mo

from sphinx.util.osutil import walk


LocaleFileInfoBase = namedtuple('CatalogInfo', 'base_dir,domain')


class CatalogInfo(LocaleFileInfoBase):

    @property
    def po_file(self):
        return self.domain + '.po'

    @property
    def mo_file(self):
        return self.domain + '.mo'

    @property
    def po_path(self):
        return path.join(self.base_dir, self.po_file)

    @property
    def mo_path(self):
        return path.join(self.base_dir, self.mo_file)

    def is_outdated(self):
        return (
            not path.exists(self.mo_path) or
            path.getmtime(self.mo_path) < path.getmtime(self.po_path))

    def write_mo(self, locale):
        with open(self.po_path, 'rt') as po:
            with open(self.mo_path, 'wb') as mo:
                write_mo(mo, read_po(po, locale))


def get_catalogs(locale_dirs, locale, gettext_compact=False, force_all=False):
    """
    :param list locale_dirs:
       list of path as `['locale_dir1', 'locale_dir2', ...]` to find
       translation catalogs. Each path contains a structure such as
       `<locale>/LC_MESSAGES/domain.po`.
    :param str locale: a language as `'en'`
    :param boolean gettext_compact:
       * False: keep domains directory structure (default).
       * True: domains in the sub directory will be merged into 1 file.
    :param boolean force_all:
       Set True if you want to get all catalogs rather than updated catalogs.
       default is False.
    :return: [CatalogInfo(), ...]
    """
    if not locale:
        return []  # locale is not specified

    catalogs = set()
    for locale_dir in locale_dirs:
        base_dir = path.join(locale_dir, locale, 'LC_MESSAGES')

        if not path.exists(base_dir):
            continue  # locale path is not found

        for dirpath, dirnames, filenames in walk(base_dir, followlinks=True):
            filenames = [f for f in filenames if f.endswith('.po')]
            for filename in filenames:
                base = path.splitext(filename)[0]
                domain = path.relpath(path.join(dirpath, base), base_dir)
                if gettext_compact and path.sep in domain:
                    domain = path.split(domain)[0]
                cat = CatalogInfo(base_dir, domain)
                if force_all or cat.is_outdated():
                    catalogs.add(cat)

    return catalogs
