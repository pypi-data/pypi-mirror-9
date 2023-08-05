# -*- coding: utf-8 -*-
u"""
    pylatex.package
    ~~~~~~~

    This module implements the class that deals with packages.

    :copyright: (c) 2014 by Jelte Fennema.
    :license: MIT, see License for more details.
"""

from __future__ import absolute_import
from .command import Command


class Package(Command):

    u"""A class that represents a package."""

    def __init__(self, name, base=u'usepackage', options=None):
        super(Package, self).__init__(base, arguments=name, options=options)
    __init__.func_annotations = {}
