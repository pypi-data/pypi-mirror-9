#!/usr/bin/python

from __future__ import absolute_import
from pylatex import Document, Section, Subsection, Table

doc = Document(filename=u"multirow")
section = Section(u'Multirow Test')

test1 = Subsection(u'Multicol')
test2 = Subsection(u'Multirow')

table1 = Table(u'|c|c|')
table1.add_hline()
table1.add_multicolumn(2, u'|c|', u'Multicol')
table1.add_hline()
table1.add_row((1, 2))
table1.add_hline()
table1.add_row((3, 4))
table1.add_hline()

table2 = Table(u'|c|c|c|')
table2.add_hline()
table2.add_multirow(3, u'*', u'Multirow', cells=((1, 2), (3, 4), (5, 6)))
table2.add_hline()
table2.add_multirow(3, u'*', u'Multirow2')
table2.add_hline()

test1.append(table1)
test2.append(table2)

section.append(test1)
section.append(test2)

doc.append(section)
doc.generate_pdf()
