# -*- coding: utf-8 -*-
u"""
    pylatex.document
    ~~~~~~~

    This module implements the class that deals with the full document.

    :copyright: (c) 2014 by Jelte Fennema.
    :license: MIT, see License for more details.
"""

from __future__ import with_statement
from __future__ import absolute_import
import os
import subprocess
from .package import Package
from .command import Command
from .utils import dumps_list
from .base_classes import BaseLaTeXContainer
from io import open


class Document(BaseLaTeXContainer):

    u"""
    A class that contains a full latex document. If needed, you can append
    stuff to the preamble or the packages if needed.
    """

    def __init__(self, filename=u'default_filename', documentclass=u'article',
                 fontenc=u'T1', inputenc=u'utf8', author=None, title=None,
                 date=None, data=None):
        self.filename = filename

        if isinstance(documentclass, Command):
            self.documentclass = documentclass
        else:
            self.documentclass = Command(u'documentclass',
                                         arguments=documentclass)

        fontenc = Package(u'fontenc', options=fontenc)
        inputenc = Package(u'inputenc', options=inputenc)
        lmodern = Package(u'lmodern')
        packages = [fontenc, inputenc, lmodern]

        self.preamble = []

        if title is not None:
            self.preamble.append(Command(u'title', title))
        if author is not None:
            self.preamble.append(Command(u'author', author))
        if date is not None:
            self.preamble.append(Command(u'date', date))

        super(Document, self).__init__(data, packages=packages)
    __init__.func_annotations = {}

    def dumps(self):
        u"""Represents the document as a string in LaTeX syntax."""
        document = ur'\begin{document}' + os.linesep

        document += super(Document, self).dumps() + os.linesep

        document += ur'\end{document}' + os.linesep

        head = self.documentclass.dumps() + os.linesep
        head += self.dumps_packages() + os.linesep
        head += dumps_list(self.preamble) + os.linesep

        return head + os.linesep + document
    dumps.func_annotations = {}

    def generate_tex(self):
        u"""Generates a .tex file."""
        with open(self.filename + u'.tex', u'w') as newf:
            self.dump(newf)
    generate_tex.func_annotations = {}

    def generate_pdf(self, clean=True):
        u"""Generates a pdf"""
        self.generate_tex()

        command = u'pdflatex --jobname="' + self.filename + u'" "' + \
            self.filename + u'.tex"'

        subprocess.check_call(command, shell=True)

        if clean:
            subprocess.call(u'rm "' + self.filename + u'.aux" "' +
                            self.filename + u'.log" "' +
                            self.filename + u'.tex"', shell=True)
    generate_pdf.func_annotations = {}
