# -*- coding: utf-8 -*-
u"""
    pylatex.graphics
    ~~~~~~~~~~~~~~~~

    This module implements the class that deals with graphics.

    :copyright: (c) 2014 by Jelte Fennema.
    :license: MIT, see License for more details.
"""

from __future__ import absolute_import
import os.path

from .utils import fix_filename, tmp_path, make_tmp
from .base_classes import BaseLaTeXNamedContainer
from .package import Package
from .command import Command


class Figure(BaseLaTeXNamedContainer):

    u"""A class that represents a Graphic."""

    def __init__(self, data=None, position=None, seperate_paragraph=True):
        u"""
        :param data:
        :param position:

        :type data: list
        :type position: str
        :param data:
        :param position:
        :param seperate_paragraph:

        :type data: list
        :type position: str
        :type seperate_paragraph: bool
        """

        packages = [Package(u'graphicx')]
        super(Figure, self).__init__(u'figure', data=data, packages=packages,
                         options=position,
                         seperate_paragraph=seperate_paragraph)
    __init__.func_annotations = {}

    def add_image(self, filename, width=ur'0.8\textwidth',
                  placement=ur'\centering'):
        u"""Adds an image.

        :param filename:
        :param width:
        :param placement:

        :type filename: str
        :type width: str
        :type placement: str
        """

        if placement is not None:
            self.append(placement)

        if width is not None:
            width = u'width=' + unicode(width)

        self.append(Command(u'includegraphics', options=width,
                            arguments=fix_filename(filename)))
    add_image.func_annotations = {}

    def add_caption(self, caption):
        u"""Adds a caption to the figure.

        :param caption:
        :type caption: str
        """

        self.append(Command(u'caption', caption))
    add_caption.func_annotations = {}


class Plt(Figure):
    u"""A class that represents a plot created with matplotlib."""

    def __init__(self, **kwargs):
        super(Plt, self).__init__(**kwargs)
    __init__.func_annotations = {}

    def _save_plot(self, plt):
        u"""Saves the plot.

        :param plt: matplotlib.pyplot
        :type plt: module

        :return: The basename with which the plot has been saved.
        :rtype: str
        """

        make_tmp()

        basename = os.path.join(tmp_path, u"plot")
        filename = u'{0}.pdf'.format(basename)

        while os.path.isfile(filename):
            basename += u"t"
            filename = u'{0}.pdf'.format(basename)

        plt.savefig(filename)

        return filename
    _save_plot.func_annotations = {}

    def add_plot(self, plt, width=ur'0.8\textwidth',
                 placement=ur'\centering'):
        u"""Adds a plot.

        :param plt: matplotlib.pyplot
        :param width: The width of the plot.
        :param placement: The placement of the plot.

        :type plt: module
        :type width: str
        :type placement: str
        """

        filename = self._save_plot(plt)

        self.add_image(filename, width, placement)
    add_plot.func_annotations = {}
