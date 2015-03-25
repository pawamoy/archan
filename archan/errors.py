# -*- coding: utf-8 -*-

# Copyright (c) 2015 Pierre Parrend
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Created on 17 fevr. 2015

@author: Pierre.Parrend
"""


class Error(Exception):
    """Base class for exceptions in this module.
    """

    def __init__(self, msg):
        self.msg = msg


class DSMError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """

    pass


class ArchanError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expr -- input expression in which the error occurred
        msg  -- explanation of the error
    """

    pass
