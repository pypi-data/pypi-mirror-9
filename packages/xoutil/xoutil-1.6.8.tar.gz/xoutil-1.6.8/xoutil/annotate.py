#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.annotate
# ---------------------------------------------------------------------
# Copyright (c) 2012-2015 Merchise Autrement
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on Apr 3, 2012

'''Provides Python 3k forward-compatible (:pep:`3107`) annotations.'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import)

from re import compile as _regex_compile
from ast import parse as _ast_parse

from six import string_types as _str_base
from xoutil.functools import partial
_ast_parse = partial(_ast_parse, filename="<annotations>", mode="eval")

from xoutil.decorator.meta import decorator

from xoutil.names import strlist as strs
__all__ = strs('annotate')
del strs


_SIGNATURE = _regex_compile(r'''(?ixm)
                            \(              # Required opening for the argumens
                            (?P<args>(.)*)
                            \)\s*           # Required close
                            (?:->\s*(?P<return>.+))?$
                            ''')

_ARG_SEP = _regex_compile(r'(?im)^\*{0,2}(?P<argname>[_\w\d]+)\s*:')


def _split_signature(signature):
    signature = (signature.strip() if isinstance(signature, _str_base) else '')
    if signature:
        matches = _SIGNATURE.match(signature)
        return matches.group('args'), matches.group('return')
    else:
        return '', None


def _parse_signature(signature):
    def _split_annotation_expression(expr):
        match = _ARG_SEP.match(expr)
        if not match:
            raise SyntaxError('Invalid signature expression %r' % expr)
        argname = match.group('argname')
        expr = expr[match.end():].lstrip()
        if not argname:
            raise SyntaxError('The signature %r is not valid' % expr)
        try:
            # This is a hack to help not implement an expression parser for
            # Python
            node = _ast_parse(expr)
            return argname, node, ''  # We consumed the whole expression
        except SyntaxError as error:
            # This probably will be a:
            #    ..., varname: expr...
            #                ^
            offset = error.offset
            while offset > 0 and expr[offset] != ',':
                offset -= 1
            if offset > 0 and expr[offset] == ',':
                return (argname, _ast_parse(expr[:offset]),
                        expr[offset + 1:].lstrip())
            else:
                raise

    class l(object):
        '''A locals implementation that skip some levels up in order to
        protect annotation's own locals.

        '''
        def __init__(self, init={}, skip_levels=5):
            import sys
            # XXX: This code is very fragile, but is the "right" thing to do
            #      in order not to leak implementation-related local variables.
            #      Any lower number will yield wrong results. For instance if
            #      skip_levels is 2, in the following case::
            #
            #          >>> args = 'args'
            #          >>> @annotate('(a: args)')
            #          ... def d():
            #          ...   pass
            #
            #      The annotation for `a` would actually get the tuple
            #      containing the string signature cause in its own
            #      implementation `annotate` uses an `args` local variable::
            #
            #          >>> d.__annotations__
            #          {'a': ('(a: args)',)}
            #
            # XXX: In fact, I should check that this does not create memory
            # references cycles with frames and stuff as noticed in the
            # CPython documentation; notwithstanding that, python's garbage
            # collector may get rid of unreachable objects, even with loops.
            self.f = f = sys._getframe(skip_levels)
            self.f_globals = f.f_globals
            self.d = dict(init)

        def __getitem__(self, key):
            from xoutil import Unset
            from xoutil.iterators import dict_update_new
            from six import PY3
            d = self.d
            res = d.get(key, Unset)
            f = self.f
            if res is Unset and f:
                f_globals = self.f_globals
                if PY3:
                    # FIXME: This modifies f_globals! Use f_builtins of the
                    # frame.

                    # In Py3k (at least Python 3.2) builtins are not directly
                    # in f_globals but inside a __builtins__ key.
                    builtins = f_globals.get('__builtins__', {})
                    dict_update_new(f_globals, builtins)
                while f and res is Unset:
                    dict_update_new(d, f.f_locals)
                    res = d.get(key, Unset)
                    f = self.f = f.f_back
                if res is Unset and f_globals:
                    dict_update_new(d, f_globals)
                    res = d.get(key, Unset)
                    # At this point there's no use to keep the reference to
                    # frames since we have reached back to the global context,
                    # so it's best to clear of reference to the last frame
                    # in order to keep this CPython-friendly.
                    self.f = None
                    self.f_globals = None
            if res:
                return res
            else:
                raise KeyError

    args, return_annotation = _split_signature(signature)
    while args:
        arg, expr, args = _split_annotation_expression(args)
        code = compile(expr, '', 'eval')
        # Don't put our globals but, just calling-frames globals
        yield arg, eval(code, None, l())
    if return_annotation:
        yield 'return', eval(return_annotation, globals(), l())


@decorator
def annotate(func, signature=None, **keyword_annotations):
    '''Annotates a function with a Python 3k forward-compatible
    ``__annotations__`` mapping.

    See :pep:`3107` for more details about annotations.


    :param signature: A string with the annotated signature of the
        decorated function.

        This string should follow the annotations syntax in :pep:`3107`. But
        there are several deviations from the PEP text:

       - There's no support for the full syntax of Python 2 expressions; in
         particular nested arguments are not supported since they are
         deprecated and are not valid in Py3k.

       - Specifying defaults is no supported (nor needed).  Defaults are
         placed in the signature of the function.

       - In the string it makes no sense to put an argument without an
         annotation, so this will raise an exception (SyntaxError).

    :param keyword_annotations: These are each mapped to a single annotation.

        Since you can't include the 'return' keyword argument for the
        annotation related with the return of the function, we provide several
        alternatives: if any of the following keywords arguments is provided
        (tested in the given order): 'return_annotation', '_return',
        '__return'; then it will be considered the 'return' annotation, the
        rest will be regarded as other annotations.

    In any of the previous cases, you may provide more (or less) annotations
    than possible by following the PEP syntax. This is not considered an error,
    since the PEP allows annotations to be modified by others means.

    If you provide a signature string **and** keywords annotations, the
    keywords will take precedence over the signature::

          >>> @annotate('() -> list', return_annotation=tuple)
          ... def otherfunction():
          ...    pass

          >>> otherfunction.__annotations__.get('return') is tuple
          True

    When parsing the `signature` the locals and globals in the context of the
    declaration are taken into account::

          >>> interface = object # let's mock of ourselves
          >>> class ISomething(interface):
          ...    pass

          >>> @annotate('(a: ISomething) -> ISomething')
          ... def somewhat(a):
          ...     return a

          >>> somewhat.__annotations__.get('a')     # doctest: +ELLIPSIS
          <class '...ISomething'>

    '''
    from xoutil.objects import pop_first_of
    func.__annotations__ = annotations = getattr(func, '__annotations__', {})
    if signature:
        annotations.update({argname: value
                            for argname, value in _parse_signature(signature)})
    probes = ('return_annotation', '_return', '__return')
    return_annotation_kwarg = pop_first_of(keyword_annotations, *probes)
    if return_annotation_kwarg:
        annotations['return'] = return_annotation_kwarg
    annotations.update(keyword_annotations)
    return func
