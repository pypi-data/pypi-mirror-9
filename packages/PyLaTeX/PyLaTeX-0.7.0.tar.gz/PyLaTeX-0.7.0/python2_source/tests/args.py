#!/usr/bin/python

u"""
    Calls functions with all available arguments to check whether they still
    exist. An error from this file means that the public API has been changed.
"""

from __future__ import absolute_import
import numpy as np
import matplotlib
matplotlib.use(u'Agg') # Not to use X server. For TravisCI.
import matplotlib.pyplot as pyplot

from pylatex import (Document, Section, Math, Table, Figure, Package, TikZ,
                    Axis, Plot, Plt)
from pylatex.command import Command
from pylatex.numpy import Matrix, VectorName
from pylatex.utils import (escape_latex, fix_filename, dumps_list, bold,
                           italic, verbatim)



# Document
doc = Document(
    default_filename=u'default_filename',
    documentclass=u'article',
    fontenc=u'T1',
    inputenc=u'utf8',
    author=u'',
    title=u'',
    date=u'',
    data=None,
    maketitle=False
)

doc.append(u'Some text.')

doc.generate_tex(filename=u'')
doc.generate_pdf(filename=u'', clean=True)

# SectionBase
s = Section(title=u'', numbering=True, data=None)

# Math
m = Math(data=None, inline=False)

# Table
t = Table(table_spec=u'|c|c|', data=None, pos=None, table_type=u'tabular')

t.add_hline(start=None, end=None)

t.add_row(cells=(1, 2), escape=False)

t.add_multicolumn(size=2, align=u'|c|', content=u'Multicol', cells=None,
                  escape=False)

t.add_multirow(size=3, align=u'*', content=u'Multirow', hlines=True, cells=None,
               escape=False)

# Command
c = Command(command=u'documentclass', arguments=None, options=None, packages=None)

# Figure
f = Figure(data=None, position=None)

f.add_image(filename=u'', width=ur'0.8\textwidth', placement=ur'\centering')

f.add_caption(caption=u'')

# Plt
plot = Plt(data=None, position=None)

x = [0, 1, 2, 3, 4, 5, 6]
y = [15, 2, 7, 1, 5, 6, 9]

pyplot.plot(x, y)

plot.add_plot(plt=pyplot, width=ur'0.8\textwidth', placement=ur'\centering')
plot.add_caption(caption=u'I am a caption.')

# Numpy
v = VectorName(name=u'')

M = np.matrix([[2, 3, 4],
               [0, 0, 1],
               [0, 0, 2]])
m = Matrix(matrix=M, name=u'', mtype=u'p', alignment=None)

# Package
p = Package(name=u'', base=u'usepackage', options=None)

# PGFPlots
tikz = TikZ(data=None)

a = Axis(data=None, options=None)

p = Plot(name=None, func=None, coordinates=None, options=None)

# Utils
escape_latex(s=u'')

fix_filename(filename=u'')

dumps_list(l=[], escape=False, token=u'\n')

bold(s=u'')

italic(s=u'')

verbatim(s=u'', delimiter=u'|')

