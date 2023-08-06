# -*- coding: utf-8 -*-
#
# This file is part of BridgeDB, a Tor bridge distribution system.
#
# :authors: Isis Lovecruft 0xA3ADB67A2CDB8B35 <isis@torproject.org>
#           please also see AUTHORS file
# :copyright: (c) 2007-2013, The Tor Project, Inc.
#             (c) 2007-2013, all entities within the AUTHORS file
# :license: 3-clause BSD, see included LICENSE for information

"""_langs.py - Storage for information on installed language support."""

RTL_LANGS = ('ar', 'he', 'fa', 'gu_IN', 'ku')


def get_langs():
    """Return a list of two-letter country codes of translations which were
    installed (if we've already been installed).
    """
    return supported


#: This list will be rewritten by :func:`get_supported_langs` in setup.py at
#: install time, so that the :attr:`bridgedb.__langs__` will hold a list of
#: two-letter country codes for languages which were installed.
supported = set(['ar', 'az', 'bg', 'ca', 'cs', 'cy', 'da', 'de', 'el', 'en', 'en_GB', 'en_US', 'eo', 'es', 'es_CL', 'eu', 'fa', 'fi', 'fr', 'fr_CA', 'gl', 'he', 'hr_HR', 'hu', 'id', 'it', 'ja', 'km', 'kn', 'ko', 'lv', 'mk', 'ms_MY', 'nb', 'nl', 'pl', 'pt', 'pt_BR', 'ro', 'ru', 'si_LK', 'sk', 'sk_SK', 'sl_SI', 'sq', 'sv', 'ta', 'th', 'tr', 'uk', 'zh_CN', 'zh_TW'])
