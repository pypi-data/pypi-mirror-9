#!/usr/bin/python

from __future__ import with_statement
from __future__ import absolute_import
from pylatex import Document, Section, Subsection, Table

doc = Document(filename=u"multirow")

with doc.create(Section(u'Multirow Test')):
    with doc.create(Subsection(u'Multicol')):
        with doc.create(Table(u'|c|c|')) as table1: # we need to keep track of the object here
            table1.add_hline()
            table1.add_multicolumn(2, u'|c|', u'Multicol')
            table1.add_hline()
            table1.add_row((1, 2))
            table1.add_hline()
            table1.add_row((3, 4))
            table1.add_hline()

    with doc.create(Subsection(u'Multirow')):
        with doc.create(Table(u'|c|c|c|')) as table2:
            table2.add_hline()
            table2.add_multirow(3, u'*', u'Multirow', cells=((1, 2), (3, 4), (5, 6)))
            table2.add_hline()
            table2.add_multirow(3, u'*', u'Multirow2')
            table2.add_hline()

doc.generate_pdf()
