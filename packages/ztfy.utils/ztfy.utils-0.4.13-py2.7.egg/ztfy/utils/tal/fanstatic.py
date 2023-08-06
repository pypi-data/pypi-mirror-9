### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008-2011 Thierry Florac <tflorac AT ulthar.net>
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

__docformat__ = "restructuredtext"

# import standard packages

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages
from zope.tales.expressions import StringExpr

# import local packages
from ztfy.utils.traversing import resolve


class FanstaticTalesExpression(StringExpr):

    def __call__(self, econtext):
        lib, res = self._expr.split('#')
        module = resolve(lib)
        resource = getattr(module, res)
        resource.need()
        return ''
