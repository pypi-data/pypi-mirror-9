##############################################################################
#
# Copyright (c) 2001, 2002 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""PY3 Compatibility module

"""
import sys
PYTHON2 = sys.version_info[0] == 2
PYTHON3 = sys.version_info[0] == 3

if PYTHON2:
    _u = unicode
    import types
    CLASS_TYPES = (type, types.ClassType)
else:
    _u = str
    CLASS_TYPES = (type,)
