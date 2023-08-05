#!/usr/bin/env python

from __future__ import absolute_import
from pylatex import Document, Section
from pylatex.graphics import Figure

doc = Document()
section = Section(u'Multirow Test')
figure = Figure()
figure.add_image(u'docs/static/screenshot.png')
figure.add_caption(u'Whoooo an imagage of a pdf')
section.append(figure)
doc.append(section)

doc.generate_pdf()
