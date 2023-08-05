#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.threading
# ---------------------------------------------------------------------
# Copyright (c) 2013-2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under
# the terms of the LICENCE attached in the distribution package.
#
# Created on 2013-05-28

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

from xoutil.modules import copy_members
threading = copy_members('threading')
del copy_members


def async_call(func, args=None, kwargs=None, callback=None, onerror=None):
    '''Executes a function `func` with the given positional and keyword
    arguments asynchronously.

    If `callback` is provided, it is called with a single positional argument:
    the result of calling `func(*args, **kwargs)`.

    If the called function ends with an exception and `onerror` is provided, it
    is called with the exception object.

    :returns: An event object that gets signalled when the function ends its
              execution whether normally or with an error.

    :rtype: :class:`threading.Event`

    '''
    event = threading.Event()
    event.clear()
    if not args:
        args = ()
    if not kwargs:
        kwargs = {}
    def async():
        try:
            result = func(*args, **kwargs)
            if callback:
                callback(result)
        except Exception as error:
            if onerror:
                onerror(error)
        finally:
            event.set()
    thread = threading.Thread(target=async)
    thread.setDaemon(True)  # XXX: Why?
    thread.start()
    return event


class _SyncronizedCaller(object):
    def __init__(self, pooling=0.005):
        self.lock = threading.RLock()
        self._not_bailed = True
        self.pooling = pooling

    def __call__(self, funcs, callback, timeout=None):
        def _syncronized_callback(result):
            with self.lock:
                if self._not_bailed:
                    callback(result)

        events, threads = [], []
        for which in funcs:
            event, thread = async_call(which, callback=_syncronized_callback)
            events.append(event)
            threads.append(thread)
        if timeout:
            def set_all_events():
                with self.lock:
                    self._not_bailed = False
                for e in events:
                    e.set()
            timer = threading.Timer(timeout, set_all_events)
            timer.start()
        while events:
            terminated = []
            for event in events:
                flag = event.wait(self.pooling)
                if flag:
                    terminated.append(event)
            for e in terminated:
                events.remove(e)
        if timeout:
            timer.cancel()


def sync_call(funcs, callback, timeout=None):
    '''Calls several functions each in it's own thread, and waits for all to
    end.

    Each time a function ends the `callback` is called (wrapped in a lock to
    avoid race conditions) with the result of the as a single positional
    argument.

    If `timeout` is not None it sould be a float number indicading the seconds
    to wait before aborting. Functions that terminated before the timeout will
    have called `callback`, but those that are still working will be ignored.

    .. todo:: Abort the execution of a thread.

    :param funcs: A sequences of callables that receive no arguments.

    '''
    sync_caller = _SyncronizedCaller()
    sync_caller(funcs, callback, timeout)
