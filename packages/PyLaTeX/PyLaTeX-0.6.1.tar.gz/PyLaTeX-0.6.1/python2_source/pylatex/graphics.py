# -*- coding: utf-8 -*-
u"""
    pylatex.graphics
    ~~~~~~~~~~~~~~~~

    This module implements the class that deals with graphics.

    :copyright: (c) 2014 by Jelte Fennema.
    :license: MIT, see License for more details.
"""

from __future__ import absolute_import
from .utils import fix_filename
from .base_classes import BaseLaTeXNamedContainer
from .package import Package
from .command import Command


class Figure(BaseLaTeXNamedContainer):

    u"""A class that represents a Graphic."""

    def __init__(self, data=None, position=None):
        packages = [Package(u'graphicx')]
        super(Figure, self).__init__(u'figure', data=data, packages=packages,
                         options=position)
    __init__.func_annotations = {}

    def add_image(self, filename, width=ur'0.8\textwidth',
                  placement=ur'\centering'):
        if placement is not None:
            self.append(placement)

        if width is not None:
            width = u'width=' + unicode(width)

        self.append(Command(u'includegraphics', options=width,
                            arguments=fix_filename(filename)))
    add_image.func_annotations = {}

    def add_caption(self, caption):
        u"""Add a caption to the figure"""
        self.append(Command(u'caption', caption))
    add_caption.func_annotations = {}
