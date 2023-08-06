#!/usr/bin/python

from __future__ import absolute_import
import numpy as np

from pylatex import Document, Section, Subsection, Math
from pylatex.numpy import Matrix, VectorName


a = np.array([[100, 10, 20]]).T

doc = Document()
section = Section(u'Numpy tests')
subsection = Subsection(u'Array')

vec = Matrix(a)
vec_name = VectorName(u'a')
math = Math(data=[vec_name, u'=', vec])

subsection.append(math)
section.append(subsection)

subsection = Subsection(u'Matrix')
M = np.matrix([[2, 3, 4],
               [0, 0, 1],
               [0, 0, 2]])
matrix = Matrix(M, mtype=u'b')
math = Math(data=[u'M=', matrix])

subsection.append(math)
section.append(subsection)


subsection = Subsection(u'Product')

math = Math(data=[u'M', vec_name, u'=', Matrix(M*a)])
subsection.append(math)

section.append(subsection)

doc.append(section)
doc.generate_pdf()
