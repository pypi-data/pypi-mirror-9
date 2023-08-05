# -*- coding: utf-8 -*-
u"""
    pylatex.command
    ~~~~~~~~~~~~~~~

    This module implements a class that implements a latex command. This can be
    used directly or it can be inherrited to make an easier interface to it.

    :copyright: (c) 2014 by Jelte Fennema.
    :license: MIT, see License for more details.
"""
from __future__ import absolute_import
from .parameters import Arguments, Options
from .base_classes import BaseLaTeXClass


class Command(BaseLaTeXClass):
    u"""
    A class that represents a command
    ::
        >>> Command('documentclass', options=Options('12pt', 'a4paper', 'twoside'), arguments='article').dumps()
        '\\documentclass[12pt,a4paper,twoside]{article}'

    """

    def __init__(self, command, arguments=None, options=None, packages=None):
        self.command = command

        if isinstance(arguments, Arguments):
            self.arguments = arguments
        elif arguments is not None:
            self.arguments = Arguments(arguments)
        else:
            self.arguments = Arguments()

        if isinstance(options, Options):
            self.options = options
        elif options is not None:
            self.options = Options(options)
        else:
            self.options = Options()

        super(Command, self).__init__(packages)
    __init__.func_annotations = {}

    def __key(self):
        return self.command, self.arguments, self.options
    __key.func_annotations = {}

    def __eq__(self, other):
        return self.__key() == other.__key()
    __eq__.func_annotations = {}

    def __hash__(self):
        return hash(self.__key())
    __hash__.func_annotations = {}

    def dumps(self):
        u"""Represents the command as a string in LaTeX syntax."""
        return u'\\{command}{options}{arguments}'.\
            format(command=self.command, options=self.options.dumps(),
                   arguments=self.arguments.dumps())
    dumps.func_annotations = {}
