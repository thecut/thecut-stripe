# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
from stripe import InvalidRequestError


class SourceIsOfWrongType(InvalidRequestError):
    """
    Raised when source of particular type has been requested, was found in
    stripe but it is not of requested type.
    To not break the code that expects particular object.

    It is subclass of :py:class:``stripe.error.InvalidRequestError`` which is
    raised when source object is not found at all.
    """

    def __init__(self, message):
        super(SourceIsOfWrongType, self).__init__(message, param=None)
