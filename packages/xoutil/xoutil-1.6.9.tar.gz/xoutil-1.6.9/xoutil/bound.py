# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.bound
# ---------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-07-21

'''Helpers for bounded execution of co-routines.

Example::

    >>> def fibonacci():
    ...   a, b = 1, 1
    ...   while True:
    ...       yield a
    ...       a, b = b, a + b

This function yields forever.  This module allows to get instances that run
until a boundary condition is met.  For instance, the `times`:func: boundary
stops after a given numbers of results are generated::

    >>> fib8 = times(8)(fibonacci)
    >>> fib8()   # the 8th fibonacci number is
    21

This is repeatable::

    >>> fib8()   # the 8th fibonacci number is
    21

    >>> fib8()   # the 8th fibonacci number is
    21

Unless you pass in a generator::

    >>> fib8 = times(8)(fibonacci())
    >>> fib8()
    21

    >>> fib8() is None
    True

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)


from types import GeneratorType
from xoutil.decorator.meta import decorator
from xoutil.objects import metaclass


class BoundedType(type):
    '''A bounded generator/function.'''
    pass


class Bounded(metaclass(BoundedType)):
    '''The bounded function.

    This is result of applying a `boundary definition` to an `unbounded
    function` (or generator).

    If `target` is a function this instance can be called several times.  If
    it's a generator then it will be closed after either calling
    (``__call__``) this instance, or consuming the generator given by
    `generate`:meth:.

    '''
    def __init__(self, target):
        self.target = target

    # The following two methods are actually implemented as closures in the
    # apply method of BoundaryCondition.  Nevertheless, they are documented
    # here as an API promise.
    def __call__(self, *args, **kwargs):
        '''Return the last value from the underlying `bounded generator`.

        '''
        raise NotImplementedError()

    def generate(self, *args, **kwargs):
        '''Return the `bounded generator`.

        This method exposes the `bounded generator`.  This allows you to "see"
        all the values yielded by the `unbounded generator` up to the point
        when the boundary condition is met.

        '''
        raise NotImplementedError()


class BoundaryCondition(object):
    '''Embodies the boundary protocol.

    The `definition` argument must a function that implements a `boundary
    definition`.  This function may take arguments to initialize the state of
    the boundary condition.

    Instances are callables that will return a `Bounded`:class: subclass
    specialized with the application of the `boundary condition` to a given
    unbounded function (`target`).  For instance, ``times(6)`` returns a
    class, that when instantiated with a `target` represents the bounded
    function that takes the 6th valued yielded by target.

    If the `definition` takes no arguments for initialization you may pass the
    `target` directly.  This is means that if `__call__`:func: receives
    arguments they will be used to instantiated the `Bounded`:class: subclass,
    ie. this case allows only a single argument `target`.

    '''
    def __new__(cls, definition, name=None):
        from types import FunctionType
        if not isinstance(definition, FunctionType):
            raise TypeError('"definition" must be a function')
        if not name:
            from xoutil.names import nameof
            name = nameof(definition, inner=True, full=True)
        result = super(BoundaryCondition, cls).__new__(cls)
        result.name = name  # needs to be set here or it'll be None
        return result

    def __init__(self, definition, name=None):
        from inspect import getargspec
        spec = getargspec(definition)
        self.args = spec[0]
        self.defaults = spec[3]
        self.varargs = spec[1]
        self.varkwargs = spec[2]
        self.definition = definition

    def __str__(self):
        return str('boundary %s(...)' % self.name)

    def __repr__(self):
        return str(self)

    @property
    def receive_args(self):
        return self.args or self.defaults or self.varargs or self.varkwargs

    def apply(self, args, kwargs):
        def execute(pred, unboundedgen, initial):
            try:
                next(pred)
                stop = pred.send(initial)
            except StopIteration:
                raise RuntimeError(
                    'Invalid boundary definition "%r"' % self.definition
                )
            try:
                while stop is not True:
                    try:
                        data = next(unboundedgen)
                        yield data
                    except (GeneratorExit, StopIteration):
                        stop = True
                    else:
                        try:
                            stop = pred.send(data)
                        except StopIteration:
                            raise RuntimeError(
                                'Invalid boundary definition "%r"' %
                                self.definition
                            )
            finally:
                pred.close()
                unboundedgen.close()

        class bounded(Bounded):
            @classmethod
            def build_pred(boundedcls):
                return self.build_generator(args, kwargs)

            def generate(me, *args, **kwargs):
                target = me.target
                if isinstance(target, GeneratorType):
                    return execute(me.build_pred(), target, None)
                else:
                    generator = target(*args, **kwargs)
                    return execute(me.build_pred(), generator, (args, kwargs))

            def __call__(me, *args, **kwargs):
                data = None
                for data in me.generate(*args, **kwargs):
                    pass
                return data

        return bounded  # return from apply()

    def build_generator(self, args, kwargs):
        if self.receive_args:
            generator = self.definition(*args, **kwargs)
        else:
            generator = self.definition()
        return generator

    def __call__(self, *args, **kwargs):
        if self.receive_args:
            return self.apply(args, kwargs)
        elif args or kwargs:
            result = self.apply((), {})(*args, **kwargs)
            if len(args) == 1:
                from functools import update_wrapper
                update_wrapper(result, args[0])
                return result
        else:
            return self.apply((), {})


@decorator
def boundary(definition, name=None, base=BoundaryCondition):
    '''Helper to define a boundary condition.

    The `definition` must be a function that returns a generator.  The
    following rules **must be** followed.  Collectively these rules are called
    the `boundary protocol`.

    - The `boundary definition` will yield True when and only when the
      boundary condition is met.  Only the value True will signal the boundary
      condition.

    - The `boundary definition` must yield at least 2 times:

      - First it will be called is ``next()`` method to allow for
        initialization of internal state.

      - Immediately after, it will be called is ``send()`` passing the tuple
        ``(args, kwargs)`` with the arguments passed to the `unbounded
        function`.  At this point the boundary definition may yield True to
        halt the execution.  In this case, the `unbounded generator` won't be
        asked for any value.

    - The `boundary definition` must yield True before terminating with a
      StopIteration.  For instance the following definition is invalid cause
      it ends without yielding True::

          @boundary
          def invalid():
              yield
              yield False

    - The `boundary definition` must deal with GeneratorExit exceptions
      properly, since we call the ``close()`` method of the generator upon
      termination.  Termination occurs when the `unbounded generator` stops by
      any means (even an error), even when the boundary condition yielded True
      or the generator itself is exhausted or there's an error in the
      generator.

      Both `whenall`:func: and `whenany`:func: call the ``close()`` method of
      all their subordinate boundary conditions.

      Most of the time this reduces to *not* catching GeneratorExit
      exceptions.

    A RuntimeError may happen if any of these rules is not followed by the
    `definition`.  Furthermore, this error will occur when invoking the
    `bounded function` and not when applying the boundary to the `unbounded
    generator`.

    '''
    from functools import update_wrapper
    result = base(definition, name=name)
    return update_wrapper(result, definition)


@boundary
def timed(maxtime):
    '''Becomes True after a given amount of time.

    The bounded generator will be allowed to yields values until the `maxtime`
    timeframe has ellapsed.

    Usage::

         @timed(timedelta(seconds=60))
         def do_something_in_about_60s():
             while True:
                 yield

    .. note:: This is a very soft limit.

       We can't actually guarrant any enforcement of the time limit.  If the
       bounded generator takes too much time or never yields this predicated
       can't do much.  This usually helps with batch processing that must not
       exceed (by too much) a given amount of time.

    The timer starts just after the ``next()`` function has been called for
    the predicate initialization.  So if the `maxtime` given is too short this
    predicated might halt the execution of the bounded function without
    allowing any processing at all.

    If `maxtime` is not a timedelta, the timedelta will be computed as
    ``timedelta(seconds=maxtime)``.

    '''
    from datetime import datetime, timedelta
    if isinstance(maxtime, timedelta):
        bound = maxtime
    else:
        bound = timedelta(seconds=maxtime)
    start = datetime.now()
    yield False  # XXX: Deal with next-send calling scheme for predicates.
    while datetime.now() - start < bound:
        yield False
    yield True   # Inform the boundary condition, or we're not compliant with
                 # the predicate protocol.


@boundary
def times(n):
    '''Becomes True after a given after the `nth` item have been produced.'''
    passed = 0
    yield False
    while passed < n:
        yield False
        passed += 1
    yield True


@boundary
def accumulated(mass, *attrs, **kwargs):
    '''Becomes True after accumulating a given "mass".

    `mass` is the maximum allowed to accumulate.  This is usually a positive
    number.  Each value produced by the `unbounded generator` is added
    together.  Yield True when this amount to more than the given `mass`.

    If any `attrs` are provided, they will be considered attributes (or keys)
    to search inside the yielded data from the bounded function.  If no
    `attrs` are provided the whole data is accumulated, so it must allow
    addition.  The attribute to be summed is extracted with
    `~xoutil.objects.get_first_of`:func:, so only the first attribute found is
    added.

    If the keyword argument `initial` is provided the accumulator is
    initialized with that value.  By default this is 0.

    '''
    from xoutil.objects import get_first_of
    accum = kwargs.pop('initial', 0)
    if kwargs:
        raise TypeError('Invalid keyword arguments %r' % kwargs.keys())
    yield False
    while accum < mass:
        data = yield False
        accum += get_first_of(data, *attrs, default=data)
    yield True


@boundary
def pred(func, skipargs=True):
    '''Predicate to allow "normal" functions to engage within the boundary
    protocol.

    `func` should take a single argument and return True if the boundary
    condition has been met.  Unlike boundary definitions themselves, this
    function will not be called with the tuple ``(args, kwargs)`` if
    `skipargs` is True, in that case only yielded values from the `unbounded
    generator` are passed.  If you need to get the original arguments, set
    `skipargs` to False.

    Example::

      >>> @pred(lambda x: x > 10)
      ... def fibonacci():
      ...     a, b = 1, 1
      ...     while True:
      ...        yield a
      ...        a, b = b, a + b

      >>> fibonacci()
      13

    '''
    sentinel = object()
    data = yield False
    if skipargs:
        data = sentinel
    while data is sentinel or not func(data):
        data = yield False
    yield True


class HighLevelBoundary(BoundaryCondition):
    '''Boundary class for high-level boundary conditions.

    The `apply` method of this only accepts the `args`, which must be
    BoundaryCondition objects or BoundedType objects (ie. an instance of a
    boundary condition), then it replaces the normal boundary condition for
    that of the high-level given the subordinate definitions.

    '''

    def apply(self, boundaries, kwargs):
        assert boundaries and not kwargs
        base = super(HighLevelBoundary, self).apply(boundaries, kwargs)

        class rebounded(base):
            @classmethod
            def build_pred(cls):
                from types import FunctionType, GeneratorType
                subordinates = []
                for bound in boundaries:
                    if isinstance(bound, FunctionType):
                        bound = boundary(bound)
                    elif isinstance(bound, GeneratorType):
                        gen = bound  # get a copy for the lambda below
                        bound = boundary(lambda: gen)
                    if isinstance(bound, BoundaryCondition):
                        if bound.receive_args:
                            raise TypeError(
                                '"%s" must be initialized' % bound.name
                            )
                        bound = bound.apply((), {})
                    if isinstance(bound, BoundedType):
                        sub = bound.build_pred()
                    else:
                        raise TypeError('Invalid argument "%r"' % bound)
                    subordinates.append(sub)
                return self.definition(*subordinates)
        return rebounded


@boundary(base=HighLevelBoundary)
def whenall(*subordinates):
    '''An AND-like boundary condition.

    It takes several boundaries and returns a single one that behaves like the
    logical AND i.e, will yield True when **all** of its subordinate boundary
    conditions have yielded True.

    It ensures that once a subordinate yields True it won't be sent anymore
    data, no matter if other subordinates keep on running and consuming data.

    Calls ``close()`` of all subordinates upon termination.

    Each `boundary` should be either:

    - A "bare" boundary definition that takes no arguments.

    - A boundary condition (i.e an instance of `BoundaryCondition`:class:).
      This is result of calling a boundary definition.

    - A generator object that complies with the boundary protocol.  This
      cannot be tested upfront, a misbehaving generator will cause a
      RuntimeError if a boundary protocol rule is not followed.

    Any other type is a TypeError.

    '''
    preds = list(subordinates)  # a copy of the list
    for pred in preds:
        next(pred)
    try:
        while preds:  # When we are out of preds it means all have yielded
                      # True
            data = yield False
            i = 0
            while preds and i < len(preds):
                pred = preds[i]
                try:
                    res = pred.send(data)
                except StopIteration:
                    raise RuntimeError('Invalid predicated in %r' % preds)
                else:
                    if res is True:
                        del preds[i]  # no more send() for this pred
                    else:
                        i += 1
        yield True
    except GeneratorExit:
        pass
    for pred in subordinates:
        pred.close()


@boundary(base=HighLevelBoundary)
def whenany(*preds):
    '''An OR-like boundary condition.

    It takes several boundaries and returns a single one that behaves like the
    logical OR, i.e, will yield True when **any** of its subordinate boundary
    conditions yield True.

    Calls ``close()`` of all subordinates upon termination.

    Each `boundary` should be either:

    - A "bare" boundary definition that takes no arguments.

    - A boundary condition (i.e an instance of `BoundaryCondition`:class:).
      This is result of calling a boundary definition.

    - A generator object that complies with the boundary protocol.  This
      cannot be tested upfront, a misbehaving generator will cause a
      RuntimeError if a boundary protocol rule is not followed.

    Any other type is a TypeError.

    '''
    for pred in preds:
        next(pred)
    stop = False
    try:
        while stop is not True:
            data = yield stop
            i, top = 0, len(preds)
            while not stop and i < top:
                pred = preds[i]
                try:
                    stop = stop or pred.send(data)
                except StopIteration:
                    raise RuntimeError('Invalid predicated in %r' % preds)
                else:
                    i += 1
        yield stop
    except GeneratorExit:
        pass
    for pred in preds:
        pred.close()


del decorator, metaclass
