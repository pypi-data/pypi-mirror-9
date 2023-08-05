# -*- coding: utf-8 -*-
"""
clik.util
=========

:copyright: (c) 2015 Joe Strickler.
:license: BSD, see LICENSE for more details.
"""
import re


def split_docstring(cls):
    parts = filter(None, re.split(r'\n\s*\n', cls.__doc__ or '', 1))
    return parts + [None] * (2 - len(parts))


class AttributeDict(dict):
    def __getattr__(self, name):
        return self[name]

    def __setattr__(self, name, value):
        self[name] = value

    def __delattr__(self, name):
        del self[name]
