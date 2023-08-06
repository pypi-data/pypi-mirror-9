#!/usr/bin/python

from __future__ import with_statement
from __future__ import absolute_import
from pylatex import Document, Section, Subsection
from pylatex.utils import italic, escape_latex


def fill_document(doc):
    u"""Adds a section, a subsection and some text to the document.

        :param doc: the document
        :type doc: :class:`pylatex.Document` instance
    """
    with doc.create(Section(u'A section')):
        doc.append(u'Some regular text and some ' + italic(u'italic text. '))

        with doc.create(Subsection(u'A subsection')):
            doc.append(escape_latex(u'Also some crazy characters: $&#{}'))
fill_document.func_annotations = {}


if __name__ == u'__main__':
    # Basic document
    doc = Document(u'basic')
    fill_document(doc)

    doc.generate_pdf()
    doc.generate_tex()

    # Document with `\maketitle` command activated
    doc = Document(author=u'Author', date=u'01/01/01', title=u'Title',
                   maketitle=True)
    fill_document(doc)

    doc.generate_pdf(u'basic_maketitle', clean=False)

    # Add stuff to the document
    doc.append(Section(u'A second section'))
    doc.append(u'Some text.')

    doc.generate_pdf(u'basic_maketitle2')
    tex = doc.dumps()  # The document as string in LaTeX syntax
