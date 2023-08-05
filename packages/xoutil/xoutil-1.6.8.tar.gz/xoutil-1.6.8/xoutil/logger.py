# -*- encoding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.logger
# ---------------------------------------------------------------------
# Copyright (c) 2014, 2015 Merchise Autrement and Contributors
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2014-06-18

'''Standard logging helpers.

'''

from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_import)

from xoutil.modules import _CustomModuleBase


class _LoggerModule(_CustomModuleBase):
    '''Standard logging helpers.

    Usage::

        logger.debug('Some debug message')


    Basically you may request any of the loggers attribute/method and this
    module will return the logger's attribute corresponding to the loggers of
    the calling module.  This avoids the boilerplate seen in most codes::

        logger = logging.getLogger(__name__)


    You may simply do::

        from xoutil.logger import debug
        debug('Some debug message')

    The proper logger will be selected by this module.

    '''
    @classmethod
    def _get_callers_module(cls, depth=2):
        import sys
        frame = sys._getframe(depth)
        try:
            return frame.f_globals['__name__']
        finally:
            frame = None

    def __getattr__(self, name):
        import logging
        logger = logging.getLogger(self._get_callers_module())
        attr = getattr(logger, name)
        return attr

    def __dir__(self):
        import logging
        logger = logging.getLogger(self._get_callers_module())
        return dir(logger)


import sys
sys.modules[__name__] = _LoggerModule(__name__)
del sys, _CustomModuleBase
