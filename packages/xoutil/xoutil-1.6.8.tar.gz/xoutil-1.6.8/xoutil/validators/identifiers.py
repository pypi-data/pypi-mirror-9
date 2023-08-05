# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.validators.identifiers
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
# Created on Nov 11, 2011

'''
Regular expressions and validation functions for several identifiers.
'''


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode)

from re import compile as _regex_compile
from six import string_types


from xoutil.names import strlist as strs
__all__ = strs('is_valid_identifier', 'is_valid_full_identifier',
               'is_valid_public_identifier',
               'is_valid_slug')
del strs


# TODO: In Py3k "ña" is a valid identifier and this regex won't allow it
_IDENTIFIER_REGEX = _regex_compile('(?i)^[_a-z][\w]*$')


def is_valid_identifier(name):
    '''Returns True if `name` a valid Python identifier.

    .. note:: Only Python 2's version of valid identifier. This means that some
              Python 3 valid identifiers are not considered valid.  This helps
              to keep things working the same in Python 2 and 3.

    '''
    return isinstance(name, string_types) and _IDENTIFIER_REGEX.match(name)


_FULL_IDENTIFIER_REGEX = _regex_compile('(?i)^[_a-z][\w]*([.][_a-z][\w]*)*$')


def is_valid_full_identifier(name):
    '''Returns True if `name` is a valid dotted Python identifier.

    See :func:`is_valid_identifier` for what "validity" means.
    '''
    return (isinstance(name, string_types) and
            _FULL_IDENTIFIER_REGEX.match(name))


_PUBLIC_IDENTIFIER_REGEX = _regex_compile('(?i)^[a-z][\w]*$')


def is_valid_public_identifier(name):
    '''Returns True if `name` is a valid Python identifier that is deemed
    public.

    Convention says that any name starting with a "_" is not public.

    See :func:`is_valid_identifier` for what "validity" means.

    '''
    return (isinstance(name, string_types) and
            _PUBLIC_IDENTIFIER_REGEX.match(name))


_SLUG_REGEX = _regex_compile('(?i)^[\w]+([-][\w]+)*$')


def is_valid_slug(slug):
    return isinstance(slug, string_types) and _SLUG_REGEX.match(slug)
