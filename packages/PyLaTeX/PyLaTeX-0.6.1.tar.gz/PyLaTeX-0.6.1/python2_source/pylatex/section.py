# -*- coding: utf-8 -*-
u"""
    pylatex.section
    ~~~~~~~

    This module implements the class that deals with sections.

    :copyright: (c) 2014 by Jelte Fennema.
    :license: MIT, see License for more details.
"""

from __future__ import absolute_import
from .utils import dumps_list
from .base_classes import BaseLaTeXContainer
from .command import Command


class SectionBase(BaseLaTeXContainer):

    u"""A class that is the base for all section type classes"""

    def __init__(self, title, numbering=True, data=None):
        self.title = title
        self.numbering = numbering

        super(SectionBase, self).__init__(data)
    __init__.func_annotations = {}

    def dumps(self):
        u"""Represents the section as a string in LaTeX syntax."""

        if not self.numbering:
            num = u'*'
        else:
            num = u''

        section_type = self.__class__.__name__.lower()
        string = Command(section_type + num, self.title).dumps()
        string += dumps_list(self)

        super(SectionBase, self).dumps()
        return string
    dumps.func_annotations = {}


class Section(SectionBase):

    u"""A class that represents a section."""


class Subsection(SectionBase):

    u"""A class that represents a subsection."""


class Subsubsection(SectionBase):

    u"""A class that represents a subsubsection."""
