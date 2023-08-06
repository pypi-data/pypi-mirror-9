#!/usr/bin/env python

from __future__ import absolute_import
from pylatex.utils import fix_filename


fname = u"aaa"
assert fix_filename(fname) == fname

fname = u"aa.a"
assert fix_filename(fname) == fname

fname = u"aa.a.a"
assert fix_filename(fname) == u"{aa.a}.a"

fname = u"abc.def.fgh.ijk"
assert fix_filename(fname) == u"{abc.def.fgh}.ijk"

fname = u"/auu/bcd/abc.def.fgh.ijk"
assert fix_filename(fname) == u"/auu/bcd/{abc.def.fgh}.ijk"

fname = u"/au.u/b.c.d/abc.def.fgh.ijk"
assert fix_filename(fname) == u"/au.u/b.c.d/{abc.def.fgh}.ijk"

fname = u"/au.u/b.c.d/abc"
assert fix_filename(fname) == u"/au.u/b.c.d/abc"
fname = u"/au.u/b.c.d/abc.def"
assert fix_filename(fname) == u"/au.u/b.c.d/abc.def"
