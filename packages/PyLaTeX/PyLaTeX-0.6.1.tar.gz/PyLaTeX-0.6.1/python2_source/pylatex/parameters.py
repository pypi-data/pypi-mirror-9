# -*- coding: utf-8 -*-
u"""
    pylatex.arguments
    ~~~~~~~

    This module implements the classes that deal with parameters, in particular
    with options and arguments.

    :copyright: (c) 2014 by Jelte Fennema.
    :license: MIT, see License for more details.
"""
from __future__ import absolute_import
from .base_classes import BaseLaTeXClass
from itertools import imap


class Parameters(BaseLaTeXClass):
    u"""
    A class implementing LaTex parameters. It supports normal positional
    parameters, as well as key-value pairs.
    Parameters can be rendered optional within square brackets ``[]`` or
    required within braces ``{}``.
    ::
        >>> args = Parameters('a', 'b', 'c')
        >>> args.dumps()
        '{a}{b}{c}'
        >>> args.optional = True
        >>> args.dumps()
        '[a,b,c]'
        >>> args = Parameters('clip', width=50, height='25em', trim='1 2 3 4')
        >>> args.optional = True
        >>> args.dumps()
        '[clip,trim=1 2 3 4,width=50,height=25em]'

    :param optional: Specifies whether this parameters are optional or not
    :type optional: bool
    """

    optional = False

    def __init__(self, *args, **kwargs):
        if len(args) == 1 and hasattr(args[0], u'__iter__') and\
                not isinstance(args[0], unicode):
            args = args[0]
        self._positional_args = list(args)
        self._key_value_args = dict(kwargs)
        super(Parameters, self).__init__(packages=None)
    __init__.func_annotations = {}

    def __key(self):
        return self.optional, tuple(self.list())
    __key.func_annotations = {}

    def __eq__(self, other):
        return self.__key() == other.__key()
    __eq__.func_annotations = {}

    def __hash__(self):
        return hash(self.__key())
    __hash__.func_annotations = {}

    def dumps(self):
        u"""
        Represents the parameters as a string in LaTeX syntax to be appended to
        a command.

        :return: The rendered parameters
        :rtype: str
        """
        params = self.list()
        if len(params) <= 0:
            return u''
        if self.optional:
            string = u'[{args}]'.format(args=u','.join(imap(unicode, params)))
        else:
            string = u'{{{args}}}'.format(args=u'}{'.join(imap(unicode, params)))
        return string
    dumps.func_annotations = {}

    def list(self):
        params = []
        params.extend(self._positional_args)
        params.extend([u'{k}={v}'.format(k=k, v=v) for k, v in
                       self._key_value_args.items()])
        return params
    list.func_annotations = {}


class Options(Parameters):
    def __init__(self, *args, **kwargs):
        super(Options, self).__init__(*args, **kwargs)
        self.optional = True
    __init__.func_annotations = {}


class Arguments(Parameters):
    def __init__(self, *args, **kwargs):
        super(Arguments, self).__init__(*args, **kwargs)
        self.optional = False
    __init__.func_annotations = {}
