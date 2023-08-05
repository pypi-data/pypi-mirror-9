# -*- coding: utf-8 -*-
"""
    pylatex.graphics
    ~~~~~~~~~~~~~~~~

    This module implements the class that deals with graphics.

    :copyright: (c) 2014 by Jelte Fennema.
    :license: MIT, see License for more details.
"""

from .utils import fix_filename
from .base_classes import BaseLaTeXNamedContainer
from .package import Package
from .command import Command


class Figure(BaseLaTeXNamedContainer):

    """A class that represents a Graphic."""

    def __init__(self, data=None, position=None):
        packages = [Package('graphicx')]
        super().__init__('figure', data=data, packages=packages,
                         options=position)

    def add_image(self, filename, width=r'0.8\textwidth',
                  placement=r'\centering'):
        if placement is not None:
            self.append(placement)

        if width is not None:
            width = 'width=' + str(width)

        self.append(Command('includegraphics', options=width,
                            arguments=fix_filename(filename)))

    def add_caption(self, caption):
        """Add a caption to the figure"""
        self.append(Command('caption', caption))
