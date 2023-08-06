#!/usr/bin/python

from __future__ import with_statement
from __future__ import absolute_import
import numpy as np

from pylatex import Document, Section, Subsection, Table, Math, TikZ, Axis, \
    Plot, Figure, Package
from pylatex.numpy import Matrix
from pylatex.utils import italic, escape_latex

doc = Document()
doc.packages.append(Package(u'geometry', options=[u'tmargin=1cm',
                                                 u'lmargin=10cm']))

with doc.create(Section(u'The simple stuff')):
    doc.append(u'Some regular text and some ' + italic(u'italic text. '))
    doc.append(escape_latex(u'\nAlso some crazy characters: $&#{}'))
    with doc.create(Subsection(u'Math that is incorrect')):
        doc.append(Math(data=[u'2*3', u'=', 9]))

    with doc.create(Subsection(u'Table of something')):
        with doc.create(Table(u'rc|cl')) as table:
            table.add_hline()
            table.add_row((1, 2, 3, 4))
            table.add_hline(1, 2)
            table.add_empty_row()
            table.add_row((4, 5, 6, 7))

a = np.array([[100, 10, 20]]).T
M = np.matrix([[2, 3, 4],
               [0, 0, 1],
               [0, 0, 2]])

with doc.create(Section(u'The fancy stuff')):
    with doc.create(Subsection(u'Correct matrix equations')):
        doc.append(Math(data=[Matrix(M), Matrix(a), u'=', Matrix(M*a)]))

    with doc.create(Subsection(u'Beautiful graphs')):
        with doc.create(TikZ()):
            plot_options = u'height=6cm, width=6cm, grid=major'
            with doc.create(Axis(options=plot_options)) as plot:
                plot.append(Plot(name=u'model', func=u'-x^5 - 242'))

                coordinates = [
                    (-4.77778, 2027.60977),
                    (-3.55556, 347.84069),
                    (-2.33333, 22.58953),
                    (-1.11111, -493.50066),
                    (0.11111, 46.66082),
                    (1.33333, -205.56286),
                    (2.55556, -341.40638),
                    (3.77778, -1169.24780),
                    (5.00000, -3269.56775),
                ]

                plot.append(Plot(name=u'estimate', coordinates=coordinates))

    with doc.create(Subsection(u'Cute kitten pictures')):
        with doc.create(Figure(position=u'h!')) as kitten_pic:
            kitten_pic.add_image(u'docs/static/kitten.jpg', width=u'120px')
            kitten_pic.add_caption(u'Look it\'s on its back')

doc.generate_pdf()
