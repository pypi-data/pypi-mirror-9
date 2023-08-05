# -*- coding: utf-8 -*-

import difflib


def udiff(a, b, fa=None, fb=None):
    r"""Returns a classical unified diff between two given strings.

    Straightforward to use::

        >>> print(udiff('a\n\nc', 'b\n\nc'))
        --- None
        +++ None
        @@ -1,3 +1,3 @@
        -a
        +b
        <BLANKLINE>
         c
        <BLANKLINE>

    Note that if the input texts do not ends with a new line, it'll be
    added automatically, so::

        >>> udiff('a', 'b') == udiff('a\n', 'b') == udiff('a', 'b\n')
        True


    """
    if not a.endswith("\n"):
        a += "\n"
    if not b.endswith("\n"):
        b += "\n"
    return "".join(
        difflib.unified_diff(
            a.splitlines(1), b.splitlines(1),
            fa, fb))
