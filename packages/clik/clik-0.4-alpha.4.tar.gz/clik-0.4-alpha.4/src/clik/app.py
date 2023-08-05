# -*- coding: utf-8 -*-
"""
clik.app
========

:copyright: (c) 2015 Joe Strickler.
:license: BSD, see LICENSE for more details.
"""
import argparse
import sys

from .globals import args, context_stack, g, parser
from .util import split_docstring, AttributeDict


class Error(Exception):
    """Base class for errors thrown from clik."""


class Command(object):
    def __init__(self, fn, name=None):
        self.children = []
        self.fn = fn
        self.name = fn.__name__ if name is None else name

    def __call__(self, fn_or_name):
        def decorate(fn, name=None):
            command = Command(fn, name)
            for other_command in self.children:
                if command.name == other_command.name:
                    raise Error('name "%s" from function %s conflicts with '
                                'name "%s" from function %s' %
                                (name, fn.__name__, other_command.name,
                                 other_command.fn.__name__))
            self.children.append(command)
            return command
        if callable(fn_or_name):
            return decorate(fn_or_name)
        return lambda fn: decorate(fn, fn_or_name)

    def configure_parser(self, parents):
        generator = self.fn()
        generator.next()
        parents = parents + [generator]
        if self.children:
            subparsers = parser.add_subparsers(title='commands')
            for child in self.children:
                description, epilog = split_docstring(child.fn)
                subparser = subparsers.add_parser(child.name,
                                                  description=description,
                                                  epilog=epilog)
                context = AttributeDict(context_stack.top)
                context.parser = subparser
                context_stack.push(context)
                child.configure_parser(parents)
                context_stack.pop()
        else:
            parser.set_defaults(_clik_commands=parents)


class App(Command):
    def main(self, argv=None, exit=sys.exit):
        if argv is None:
            argv = sys.argv

        context = AttributeDict(**{
            'args': None,
            'g': AttributeDict(app=self, argv=argv),
            'parser': None
        })
        context_stack.push(context)

        try:
            description, epilog = split_docstring(self.fn)
            context.parser = argparse.ArgumentParser(prog=self.name,
                                                     description=description,
                                                     epilog=epilog)
            self.configure_parser([])
            try:
                context.args = parser.parse_args(argv[1:])
            except SystemExit, e:
                rv = e.code
            else:
                for node in args._clik_commands:
                    try:
                        rv = node.send(context)
                    except StopIteration:
                        rv = 0
                    if rv:
                        break
                for node in reversed(args._clik_commands[:-1]):
                    try:
                        node.send(context)
                    except StopIteration:
                        pass
            exit(rv)
        finally:
            context_stack.pop()


def app(fn_or_name):
    if callable(fn_or_name):
        return App(fn_or_name)
    return lambda fn: App(fn, fn_or_name)
