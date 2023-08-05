# -*- coding: utf-8 -*-
"""
    pyrseas.lib.pycompat
    ~~~~~~~~~~~~~~~~~~~~

    Helpers for compatibility between Python 2.x and 3.x.
"""
import sys

PY2 = sys.version_info[0] == 2

if not PY2:
    strtypes = (str, )
else:
    strtypes = (str, unicode)
