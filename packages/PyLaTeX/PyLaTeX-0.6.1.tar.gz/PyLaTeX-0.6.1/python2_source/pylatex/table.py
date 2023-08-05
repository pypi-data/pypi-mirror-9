# -*- coding: utf-8 -*-
u"""
    pylatex.table
    ~~~~~~~

    This module implements the class that deals with tables.

    :copyright: (c) 2014 by Jelte Fennema.
    :license: MIT, see License for more details.
"""

from __future__ import absolute_import
from .utils import dumps_list
from .base_classes import BaseLaTeXNamedContainer
from .package import Package
from .command import Command

from collections import Counter
import re


def get_table_width(table_spec):
    column_letters = [u'l', u'c', u'r', u'p', u'm', u'b']

    # Remove things like {\bfseries}
    cleaner_spec = re.sub(ur'{[^}]*}', u'', table_spec)
    spec_counter = Counter(cleaner_spec)

    return sum(spec_counter[l] for l in column_letters)
get_table_width.func_annotations = {}


class Table(BaseLaTeXNamedContainer):

    u"""A class that represents a table."""

    def __init__(self, table_spec, data=None, pos=None, table_type=u'tabular',
                 **kwargs):
        self.width = get_table_width(table_spec)

        super(Table, self).__init__(table_type, data=data, options=pos,
                         argument=table_spec, **kwargs)
    __init__.func_annotations = {}

    def add_hline(self, start=None, end=None):
        u"""Add a horizontal line to the table"""
        if start is None and end is None:
            self.append(ur'\hline')
        else:
            if start is None:
                start = 1
            elif end is None:
                end = self.width
            self.append(Command(u'cline', unicode(start) + u'-' + unicode(end)))
    add_hline.func_annotations = {}

    def add_empty_row(self):
        u"""Add an empty row to the table"""
        self.append((self.width - 1) * u'&' + ur'\\')
    add_empty_row.func_annotations = {}

    def add_row(self, cells, escape=False):
        u"""Add a row of cells to the table"""
        self.append(dumps_list(cells, escape=escape, token=u'&') + ur'\\')
    add_row.func_annotations = {}

    def add_multicolumn(self, size, align, content, cells=None, escape=False):
        u"""
        Add a multicolumn of width size to the table, with cell content content
        """
        self.append(Command(u'multicolumn', arguments=(size, align, content)))
        if cells is not None:
            self.add_row(cells)
        else:
            self.append(ur'\\')
    add_multicolumn.func_annotations = {}

    def add_multirow(self, size, align, content, hlines=True, cells=None,
                     escape=False):
        u"""
        Add a multirow of height size to the table, with cell content content
        """
        self.append(Command(u'multirow', arguments=(size, align, content)))
        self.packages.add(Package(u'multirow'))
        if cells is not None:
            for i, row in enumerate(cells):
                if hlines and i:
                    self.add_hline(2)
                self.append(u'&')
                self.add_row(row)
        else:
            for i in xrange(size):
                self.add_empty_row()
    add_multirow.func_annotations = {}


class Tabu(Table):

    u"""A class that represents a tabu (more flexible table)"""

    def __init__(self, *args, **kwargs):
        super(Tabu, self).__init__(*args, table_type=u'tabu', packages=[Package(u'tabu')],
                         **kwargs)
    __init__.func_annotations = {}


class LongTable(Table):

    u"""A class that represents a longtable (multipage table)"""

    def __init__(self, *args, **kwargs):
        super(LongTable, self).__init__(*args, table_type=u'longtable',
                         packages=[Package(u'longtable')], **kwargs)
    __init__.func_annotations = {}


class LongTabu(Table):

    u"""A class that represents a longtabu (more flexible multipage table)"""

    def __init__(self, *args, **kwargs):
        packages = [Package(u'tabu'), Package(u'longtable')]
        super(LongTabu, self).__init__(*args, table_type=u'longtabu', packages=packages,
                         **kwargs)
    __init__.func_annotations = {}
