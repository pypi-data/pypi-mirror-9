#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ---------------------------------------------------------------------
# xoutil.release
# ---------------------------------------------------------------------
# Copyright (c) 2013-2015 Merchise Autrement and Contributors
# Copyright (c) 2012 Medardo Rodríguez
# All rights reserved.
#
# This is free software; you can redistribute it and/or modify it under the
# terms of the LICENCE attached (see LICENCE file) in the distribution
# package.
#
# Created on 2012-04-01


from __future__ import (division as _py3_division,
                        print_function as _py3_print,
                        unicode_literals as _py3_unicode,
                        absolute_import as _py3_abs_imports)

VERSION = '1.6.9'


def dev_tag():
    result = ''
    import os
    fn = os.path.abspath(os.path.join(__file__, '..', '..', 'setup.cfg'))
    if os.path.exists(fn):
        try:
            import configparser
        except:
            # Python 2.7
            import ConfigParser as configparser
        parser = configparser.SafeConfigParser()
        parser.read([fn])
        try:
            res = parser.get(str('egg_info'), str('tag_build'))
        except:
            res = None
        if res:
            result = res
    return result


def dev_tag_installed():
    import re
    import pkg_resources
    tag_start_regex = re.compile(r'[^\d\.]')
    try:
        dist = pkg_resources.get_distribution('xoutil')
        version = dist.version
        match = tag_start_regex.search(version)
        if match:
            return version[match.start():]
        else:
            return None
    except:
        return None


RELEASE_TAG = dev_tag_installed() or dev_tag()
