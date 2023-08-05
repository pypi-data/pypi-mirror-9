# -*- coding: utf-8 -*-

from __future__ import print_function


import textwrap
import re


def dedent(txt):
    """Dedent a txt, tolerating first line not indented.

        >>> from __future__ import print_function

    Various issues should be tackled:

        >>> print(dedent(
        ...    '''This is a doc
        ...
        ...       with fancy indentation, that should just work also.
        ...       Without removing too much neither as:
        ...          - more space.'''))
        This is a doc
        <BLANKLINE>
        with fancy indentation, that should just work also.
        Without removing too much neither as:
           - more space.

    Note that the first line doesn't have indentation and neither the
    second (which is empty).

    Of course, ``dedent`` should not fail on empty string neither:

        >>> dedent("")
        ''

    """
    if "\n" not in txt:
        return txt.lstrip()
    first_line, end = txt.split('\n', 1)
    return "%s\n%s" % (first_line, textwrap.dedent(end))


## Note that a quite equivalent function was added to textwrap in python 3.3
def indent(text, prefix="  ", first=None):
    """Return text string indented with the given prefix

    >>> string = 'This is first line.\\nThis is second line\\n'

    >>> print(indent(string, prefix="| "))
    | This is first line.
    | This is second line
    |

    >>> print(indent(string, first="- "))
    - This is first line.
      This is second line

    >>> print(indent(string, first=""))  ## doctest: -NORMALIZE_WHITESPACE
    This is first line.
      This is second line
    <BLANKLINE>

    """
    if first is not None:
        first_line = text.split("\n")[0]
        rest = '\n'.join(text.split("\n")[1:])
        return '\n'.join([first + first_line,
                          indent(rest, prefix=prefix)])
    return '\n'.join([prefix + line
                      for line in text.split('\n')])


def paragraph_wrap(text, regexp="\n\n"):
    r"""Wrap text by making sure that paragraph are separated correctly

    >>> string = 'This is first paragraph which is quite long don\'t you \
    ... think ? Well, I think so.\n\nThis is second paragraph\n'

    >>> print(paragraph_wrap(string)) # doctest: +NORMALIZE_WHITESPACE
    This is first paragraph which is quite long don't you think ? Well, I
    think so.
    This is second paragraph

    Notice that that each paragraph has been wrapped separately.

    """
    regexp = re.compile(regexp, re.MULTILINE)
    return "\n".join("\n".join(textwrap.wrap(paragraph.strip()))
                     for paragraph in regexp.split(text)).strip()


def ucfirst(msg):
    """Return altered msg where only first letter was forced to uppercase."""
    return msg[0].upper() + msg[1:]


## Provided in textwrap.shorten in python 3
def shorten(s, l):
    """Return given string truncated to given length."""
    if len(s) > l:
        return s[:l - 2] + ".."
    return s


truncate = shorten
