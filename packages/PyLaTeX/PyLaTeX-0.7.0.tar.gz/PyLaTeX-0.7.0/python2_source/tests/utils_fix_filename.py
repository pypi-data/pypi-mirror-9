#!/usr/bin/env python

from __future__ import absolute_import
from pylatex.utils import fix_filename


fname = u"aaa"
assert fix_filename(fname) == fname

fname = u"aa.a"
assert fix_filename(fname) == fname

fname = u"aa.a.a"
assert fix_filename(fname) == u"{aa.a}.a"
