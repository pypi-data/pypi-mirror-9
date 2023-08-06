# -*- coding: utf-8 -*-
"""
clik.app
========

:copyright: (c) 2015 Joe Strickler.
:license: BSD, see LICENSE for more details.
"""
import argparse
import sys

from .globals import args, context_stack, parser, subcommand
from .util import split_docstring, AttributeDict


class Error(Exception):
    """Base class for errors thrown from clik."""


class NameConflictError(Error):
    """Raised when trying to add two subcommands with conflicting names."""
    def __init__(self, name, fn, other):
        fmt = 'name "%s" from function %s conflicts with "%s" from function %s'
        msg = fmt % (name, fn.__name__, other.name, other.fn.__name__)
        super(NameConflictError, self).__init__(msg)


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
                    raise NameConflictError(name, fn, other_command)
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
                subparser = subparsers.add_parser(
                    child.name,
                    description=description,
                    epilog=epilog,
                )
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

        context = AttributeDict(
            args=None,
            g=AttributeDict(app=self, argv=argv),
            parser=None,
            subcommand=None,
        )
        context_stack.push(context)

        try:
            description, epilog = split_docstring(self.fn)
            context.parser = argparse.ArgumentParser(
                prog=self.name,
                description=description,
                epilog=epilog,
            )
            self.configure_parser([])

            try:
                context.args = parser.parse_args(argv[1:])
            except SystemExit, e:
                rv = e.code
            else:
                rvs = []

                def make_subcommand(next_node, context):
                    def run_subcommand():
                        context_stack.pop()
                        try:
                            rvs.append(next_node.send(context))
                        except StopIteration:
                            subcommand()
                            rvs.append(0)
                        return not any(rvs)
                    return run_subcommand

                stack = []
                for i, node in enumerate(args._clik_commands[:-1]):
                    next_node = args._clik_commands[i + 1]
                    context.subcommand = make_subcommand(next_node, context)
                    stack.append(context)
                    context = AttributeDict(context)
                context.subcommand = lambda: 0
                stack.append(context)
                for context in reversed(stack):
                    context_stack.push(context)

                try:
                    rvs.append(args._clik_commands[0].send(context))
                except StopIteration:
                    if len(args._clik_commands) > 1:
                        subcommand()
                    rvs.append(0)

                for rv in rvs:
                    if rv:
                        break
                else:
                    rv = 0

            exit(rv)
        finally:
            context_stack.pop()


def app(fn_or_name):
    if callable(fn_or_name):
        return App(fn_or_name)
    return lambda fn: App(fn, fn_or_name)
