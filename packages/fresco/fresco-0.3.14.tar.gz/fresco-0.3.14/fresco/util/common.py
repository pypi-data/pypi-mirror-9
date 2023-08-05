#
# Copyright (c) 2014 Oliver Cope. All rights reserved.
# See LICENSE.txt for terms of redistribution and use.

"""
Common utilities for writing applications in fresco
"""
from __future__ import absolute_import

from fresco.exceptions import NotFound

__all__ = ['object_or_404']


def object_or_404(ob, exception=NotFound):
    """
    Return the value of ``ob`` if it is not None. Otherwise raise a NotFound
    exception.
    """
    if ob is None:
        raise exception()
    return ob
