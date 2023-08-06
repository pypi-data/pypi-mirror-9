#!/usr/bin/env python

from __future__ import absolute_import
from pylatex import Document, Section
from pylatex.utils import escape_latex

doc = Document(default_filename=u"utils_escape_latex")
section = Section(u'Escape LaTeX characters test')

text = escape_latex(u'''\
& (ampersand)
% (percent)
$ (dollar)
# (number)
_ (underscore)
{ (left curly brace)
} (right curly brace)
~ (tilde)
^ (caret)
\\ (backslash)
--- (three minuses)
a\xA0a (non breaking space)
''')

section.append(text)
doc.append(section)

doc.generate_pdf()
