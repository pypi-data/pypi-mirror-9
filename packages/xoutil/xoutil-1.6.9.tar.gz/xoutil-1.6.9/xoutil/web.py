# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xotl.web
# ---------------------------------------------------------------------
# Copyright (c) 2013-2015 Merchise Autrement and Contributors
# Copyright (c) 2011, 2012 Medardo Rodríguez
# All rights reserved.
#
# Author: Medardo Rodriguez
# Contributors: see CONTRIBUTORS and HISTORY file
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on Jun 28, 2011

'''Utils for Web applications.'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

from xoutil.names import strlist as strs
__all__ = strs('slugify')
del strs


def slugify(s, entities=True, decimal=True, hexadecimal=True):
    '''
    Normalizes string, converts to lower-case, removes non-alpha characters,
    and converts spaces to hyphens.

    Parts from http://www.djangosnippets.org/snippets/369/

        >>> slugify("Manuel Vázquez Acosta")    # doctest: +SKIP
        'manuel-vazquez-acosta'

    If `s` and `entities` is True (the default) all HTML entities
    are replaced by its equivalent character before normalization::

        >>> slugify("Manuel V&aacute;zquez Acosta")   # doctest: +SKIP
        'manuel-vazquez-acosta'

    If `entities` is False, then no HTML-entities substitution is made::

        >>> value = "Manuel V&aacute;zquez Acosta"
        >>> slugify(value, entities=False)  # doctest: +SKIP
        'manuel-v-aacute-zquez-acosta'

    If `decimal` is True, then all entities of the form ``&#nnnn`` where
    `nnnn` is a decimal number deemed as a unicode codepoint, are replaced by
    the corresponding unicode character::

        >>> slugify('Manuel V&#225;zquez Acosta')  # doctest: +SKIP
        'manuel-vazquez-acosta'

        >>> value = 'Manuel V&#225;zquez Acosta'
        >>> slugify(value, decimal=False)  # doctest: +SKIP
        'manuel-v-225-zquez-acosta'


    If `hexadecimal` is True, then all entities of the form ``&#nnnn`` where
    `nnnn` is a hexdecimal number deemed as a unicode codepoint, are replaced
    by the corresponding unicode character::

        >>> slugify('Manuel V&#x00e1;zquez Acosta')  # doctest: +SKIP
        'manuel-vazquez-acosta'

        >>> slugify('Manuel V&#x00e1;zquez Acosta', hexadecimal=False)  # doctest: +SKIP
        'manuel-v-x00e1-zquez-acosta'

    '''
    import re
    from six import unichr
    from xoutil.string import _unicode, safe_decode, normalize_slug
    if not isinstance(s, _unicode):
        s = safe_decode(s)
    if entities:
        try:
            from htmlentitydefs import name2codepoint
        except ImportError:
            # Py3k: The ``htmlentitydefs`` module has been renamed to
            # ``html.entities`` in Python 3
            from html.entities import name2codepoint
        s = re.sub(str('&(%s);') % str('|').join(name2codepoint),
                   lambda m: unichr(name2codepoint[m.group(1)]), s)
    if decimal:
        try:
            s = re.sub(r'&#(\d+);', lambda m: unichr(int(m.group(1))), s)
        except:
            pass
    if hexadecimal:
        try:
            s = re.sub(r'&#x([\da-fA-F]+);',
                       lambda m: unichr(int(m.group(1), 16)), s)
        except:
            pass
    return normalize_slug(s, '-')
