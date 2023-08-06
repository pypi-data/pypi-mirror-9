### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2008 Thierry Florac <tflorac AT ulthar.net>
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


# import standard packages
import functools
import warnings

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages


def deprecated(*msg):
    """This is a decorator which can be used to mark functions
    as deprecated. It will result in a warning being emitted
    when the function is used.
    """

    def decorator(func):

        @functools.wraps(func)
        def new_func(*args, **kwargs):
            warnings.warn_explicit("Function %s is deprecated. %s" % (func.__name__, message),
                                   category=DeprecationWarning,
                                   filename=func.func_code.co_filename,
                                   lineno=func.func_code.co_firstlineno + 1)
            return func(*args, **kwargs)
        return new_func

    if len(msg) == 1 and callable(msg[0]):
        message = u''
        return decorator(msg[0])
    else:
        message = msg[0]
        return decorator
