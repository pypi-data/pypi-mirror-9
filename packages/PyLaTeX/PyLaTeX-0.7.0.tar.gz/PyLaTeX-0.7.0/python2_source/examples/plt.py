#!/usr/bin/python

from __future__ import with_statement
from __future__ import absolute_import
import matplotlib
matplotlib.use(u'Agg') # Not to use X server. For TravisCI.
import matplotlib.pyplot as pyplot

from pylatex import Document, Section, Plt



if __name__ == u'__main__':
    x = [0, 1, 2, 3, 4, 5, 6]
    y = [15, 2, 7, 1, 5, 6, 9]

    pyplot.plot(x, y)

    doc = Document(u'matplolib_pdf')
    doc.append(u'Introduction.')

    with doc.create(Section(u'I am a section')):
        doc.append(u'Take a look at this beautiful plot:')

        with doc.create(Plt(position=u'htbp')) as plot:
            plot.add_plot(pyplot)
            plot.add_caption(u'I am a caption.')

        doc.append(u'Created using matplotlib.')

    doc.append(u'Conclusion.')

    doc.generate_pdf()
