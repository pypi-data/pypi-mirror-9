# -*- coding: utf-8 -*-
u"""
    pylatex.utils
    ~~~~~~~

    This module implements some simple functions with all kinds of
    functionality.

    :copyright: (c) 2014 by Jelte Fennema.
    :license: MIT, see License for more details.
"""

from __future__ import absolute_import
import os.path
import shutil



_latex_special_chars = {
    u'&':  ur'\&',
    u'%':  ur'\%',
    u'$':  ur'\$',
    u'#':  ur'\#',
    u'_':  ur'\_',
    u'{':  ur'\{',
    u'}':  ur'\}',
    u'~':  ur'\textasciitilde{}',
    u'^':  ur'\^{}',
    u'\\': ur'\textbackslash{}',
    u'\n': ur'\\',
    u'-':  ur'{-}',
    u'\xA0': u'~',  # Non-breaking space
}

tmp_path = os.path.normpath(
    os.path.join(
        os.path.dirname(
            os.path.realpath(__file__)
        ),
        u"..",
        u"tmp"
    )
)


def escape_latex(s):
    u"""Escape characters that are special in latex.

    Sources:
        * http://tex.stackexchange.com/a/34586/43228
        * http://stackoverflow.com/a/16264094/2570866

        :param s:

        :type s: str

        :return:
        :rtype: str
    """

    return u''.join(_latex_special_chars.get(c, c) for c in s)
escape_latex.func_annotations = {}


def fix_filename(filename):
    u"""Latex has problems if there are one or more points in the filename,
    thus 'abc.def.jpg' will be changed to '{abc.def}.jpg

        :param filename:

        :type filename: str

        :return:
        :rtype: str
    """

    parts = filename.split(u'.')

    if len(parts) > 2:
        return u'{' + u'.'.join(parts[0:-1]) + u'}.' + parts[-1]
    else:
        return filename
fix_filename.func_annotations = {}


def dumps_list(l, escape=False, token=u'\n'):
    u"""Dumps a list that can contain anything.

        :param l:
        :param escape:
        :param token:

        :type l: list
        :type escape: bool
        :type token: str

        :return:
        :rtype: str
    """

    return token.join(_latex_item_to_string(i, escape) for i in l)
dumps_list.func_annotations = {}


def _latex_item_to_string(i, escape=False):
    u"""Uses the render method when possible, otherwise uses str.

        :param i:
        :param escape:

        :type i: object
        :type escape: bool

        :return:
        :rtype: str
    """

    if hasattr(i, u'dumps'):
        return i.dumps()
    elif escape:
        return unicode(escape_latex(i))

    return unicode(i)
_latex_item_to_string.func_annotations = {}


def bold(s):
    u"""Returns the string bold.

    Source: http://stackoverflow.com/a/16264094/2570866

        :param s:

        :type s: str

        :return:
        :rtype: str
    """

    return ur'\textbf{' + s + u'}'
bold.func_annotations = {}


def italic(s):
    u"""Returns the string italicized.

    Source: http://stackoverflow.com/a/16264094/2570866

        :param s:

        :type s: str

        :return:
        :rtype: str
    """

    return ur'\textit{' + s + u'}'
italic.func_annotations = {}


def verbatim(s, delimiter=u'|'):
    u"""Returns the string verbatim.

        :param s:
        :param delimiter:

        :type s: str
        :type delimiter: str

        :return:
        :rtype: str
    """

    return ur'\verb' + delimiter + s + delimiter
verbatim.func_annotations = {}


def make_tmp():
    u"""Creates the tmp directory if it doesn't exist."""

    if not os.path.exists(tmp_path):
        os.makedirs(tmp_path)
make_tmp.func_annotations = {}

def rm_tmp():
    u"""Removes the tmp directory."""

    if os.path.exists(tmp_path):
        shutil.rmtree(tmp_path)
rm_tmp.func_annotations = {}
