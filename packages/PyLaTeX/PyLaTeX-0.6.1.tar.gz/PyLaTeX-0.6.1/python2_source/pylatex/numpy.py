# -*- coding: utf-8 -*-
u"""
    pylatex.numpy
    ~~~~~~~~~~~~~

    This module implements the classes that deals with numpy objects.

    :copyright: (c) 2014 by Jelte Fennema.
    :license: MIT, see License for more details.
"""

from __future__ import absolute_import
import numpy as np
from pylatex.base_classes import BaseLaTeXClass
from pylatex.package import Package
from pylatex.command import Command


class VectorName(Command):
    def __init__(self, name):
        super(VectorName, self).__init__(u'mathbf', arguments=name)
    __init__.func_annotations = {}


class Matrix(BaseLaTeXClass):
    def __init__(self, matrix, name=u'', mtype=u'p', alignment=None):
        self.mtype = mtype
        self.matrix = matrix
        self.alignment = alignment
        self.name = name

        super(Matrix, self).__init__(packages=[Package(u'amsmath')])
    __init__.func_annotations = {}

    def dumps(self):
        string = ur'\begin{'
        mtype = self.mtype + u'matrix'

        if self.alignment is not None:
            mtype += u'*'
            alignment = u'{' + self.alignment + u'}'
        else:
            alignment = u''

        string += mtype + u'}' + alignment
        string += u'\n'

        shape = self.matrix.shape

        for (y, x), value in np.ndenumerate(self.matrix):
            if x:
                string += u'&'
            string += unicode(value)

            if x == shape[1] - 1 and y != shape[0] - 1:
                string += ur'\\' + u'\n'

        string += u'\n'

        string += ur'\end{' + mtype + u'}'

        super(Matrix, self).dumps()
        return string
    dumps.func_annotations = {}
