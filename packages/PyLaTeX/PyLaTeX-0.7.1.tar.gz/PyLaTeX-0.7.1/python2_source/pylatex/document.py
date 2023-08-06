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
from .utils import dumps_list, rm_tmp
from .base_classes import BaseLaTeXContainer
from io import open


class Document(BaseLaTeXContainer):

    u"""
    A class that contains a full LaTeX document. If needed, you can append
    stuff to the preamble or the packages.
    """

    def __init__(self, default_filename=u'default_filename',
                 documentclass=u'article', fontenc=u'T1', inputenc=u'utf8',
                 author=u'', title=u'', date=u'', data=None, maketitle=False):
        u"""
            :param default_filename: the default filename to save files
            :param documentclass: the LaTeX class of the document
            :param fontenc: the option for the fontenc package
            :param inputenc: the option for the inputenc package
            :param author: the author of the document
            :param title: the title of the document
            :param date: the date of the document
            :param data:
            :param maketitle: whether `\maketitle` command is activated or not.

            :type default_filename: str
            :type documentclass: str or :class:`command.Command` instance
            :type fontenc: str
            :type inputenc: str
            :type author: str
            :type title: str
            :type date: str
            :type data: list
            :type maketitle: bool
        """

        self.default_filename = default_filename
        self.maketitle = maketitle

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

        self.preamble.append(Command(u'title', title))
        self.preamble.append(Command(u'author', author))
        self.preamble.append(Command(u'date', date))

        super(Document, self).__init__(data, packages=packages)
    __init__.func_annotations = {}

    def dumps(self):
        u"""Represents the document as a string in LaTeX syntax.

            :return:
            :rtype: str
        """

        document = ur'\begin{document}' + os.linesep

        if self.maketitle:
            document += ur'\maketitle' + os.linesep

        document += super(Document, self).dumps() + os.linesep

        document += ur'\end{document}' + os.linesep

        head = self.documentclass.dumps() + os.linesep
        head += self.dumps_packages() + os.linesep
        head += dumps_list(self.preamble) + os.linesep

        return head + os.linesep + document
    dumps.func_annotations = {}

    def generate_tex(self, filename=u''):
        u"""Generates a .tex file.

            :param filename: the name of the file

            :type filename: str
        """

        filename = self.select_filename(filename)

        with open(filename + u'.tex', u'w') as newf:
            self.dump(newf)
    generate_tex.func_annotations = {}

    def generate_pdf(self, filename=u'', clean=True, compiler=u'pdflatex'):
        u"""Generates a .pdf file.

            :param filename: the name of the file
            :param clean: whether non-pdf files created by `pdflatex` must be
            removed or not

            :type filename: str
            :type clean: bool
        """

        filename = self.select_filename(filename)

        self.generate_tex(filename)

        command = compiler + u' --jobname="' + filename + u'" "' + \
            filename + u'.tex"'

        subprocess.check_call(command, shell=True)

        if clean:
            subprocess.call(u'rm "' + filename + u'.aux"', shell=True)
            subprocess.call(u'rm "' + filename + u'.log"', shell=True)
            subprocess.call(u'rm "' + filename + u'.tex"', shell=True)
            subprocess.call(u'rm "' + filename + u'.out"', shell=True)

        rm_tmp()
    generate_pdf.func_annotations = {}

    def select_filename(self, filename):
        u"""Makes a choice between `filename` and `self.default_filename`.

            :param filename: the filename to be compared with
            `self.default_filename`

            :type filename: str

            :return: The selected filename
            :rtype: str
        """

        if filename == u'':
            return self.default_filename
        else:
            return filename
    select_filename.func_annotations = {}
