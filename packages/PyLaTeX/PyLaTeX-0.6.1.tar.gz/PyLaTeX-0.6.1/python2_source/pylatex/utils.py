# -*- coding: utf-8 -*-
u"""
    pylatex.utils
    ~~~~~~~

    This module implements some simple functions with all kinds of
    functionality.

    :copyright: (c) 2014 by Jelte Fennema.
    :license: MIT, see License for more details.
"""

_latex_special_chars = {
    u'&':  ur'\&',
    u'%':  ur'\%',
    u'$':  ur'\$',
    u'#':  ur'\#',
    u'_':  ur'\_',
    u'{':  ur'\{',
    u'}':  ur'\}',
    u'~':  ur'\lettertilde{}',
    u'^':  ur'\letterhat{}',
    u'\\': ur'\letterbackslash{}',
    u'\n': ur'\\\\',
}


def escape_latex(s):
    u"""Escape characters that are special in latex.

    Sources:
        * http://tex.stackexchange.com/a/34586/43228
        * http://stackoverflow.com/a/16264094/2570866
    """
    return u''.join(_latex_special_chars.get(c, c) for c in s)
escape_latex.func_annotations = {}


def fix_filename(filename):
    u"""Latex has problems if there are one or more points in the filename,
    thus 'abc.def.jpg' will be changed to '{abc.def}.jpg
    """
    parts = filename.split(u'.')
    return u'{' + u'.'.join(parts[0:-1]) + u'}.' + parts[-1]
fix_filename.func_annotations = {}


def dumps_list(l, escape=False, token=u'\n'):
    u"""Dumps a list that can contain anything"""
    return token.join(_latex_item_to_string(i, escape) for i in l)
dumps_list.func_annotations = {}


def _latex_item_to_string(i, escape=False):
    u"""Use the render method when possible, otherwise use str."""
    if hasattr(i, u'dumps'):
        return i.dumps()
    elif escape:
        return unicode(escape_latex(i))
    return unicode(i)
_latex_item_to_string.func_annotations = {}


def bold(s):
    u"""Returns the string bold.

    Source: http://stackoverflow.com/a/16264094/2570866
    """
    return ur'\textbf{' + s + u'}'
bold.func_annotations = {}


def italic(s):
    u"""Returns the string italicized.

    Source: http://stackoverflow.com/a/16264094/2570866
    """
    return ur'\textit{' + s + u'}'
italic.func_annotations = {}


def verbatim(s, delimiter=u'|'):
    u"""Returns the string verbatim."""
    return ur'\verb' + delimiter + s + delimiter
verbatim.func_annotations = {}
