# -*- coding: utf-8 -*-

"""
Errors module.

Contains DSMError and ArchanError.
"""


class DSMError(Exception):
    """
    Exception raised for errors in the input.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """


class ArchanError(Exception):
    """
    Exception raised for errors in the input.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """
