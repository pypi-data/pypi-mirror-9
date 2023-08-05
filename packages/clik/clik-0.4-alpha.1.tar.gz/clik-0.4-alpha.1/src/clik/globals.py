# -*- coding: utf-8 -*-
"""
clik.globals
============

:copyright: (c) 2015 Joe Strickler.
:license: BSD, see LICENSE for more details.
"""
from functools import partial
from .local import LocalProxy, LocalStack


context_stack = LocalStack()


def lookup_object(name):
    if context_stack.top is None:
        raise RuntimeError('working outside of invocation context')
    return getattr(context_stack.top, name)


def make_global(key):
    return LocalProxy(partial(lookup_object, key))


args = make_global('args')
g = make_global('g')
parser = make_global('parser')
