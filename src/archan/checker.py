# -*- coding: utf-8 -*-

# Copyright (c) 2015 Pierre Parrend
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Created on 8 janv. 2015

@author: Pierre.Parrend
"""

from __future__ import unicode_literals

from archan.criterion import CRITERIA, Criterion


class Archan(object):
    """Architecture analyser class."""
    def __init__(self, criteria=None):

        if criteria is None:
            criteria = CRITERIA
        self.criteria = criteria

    def check(self, dsm, criteria=None):
        if criteria:
            return {
                criterion.codename:
                    criterion(dsm)
                    if criterion in criteria
                    else (Criterion.IGNORED, '')
                for criterion in self.criteria
            }
        else:
            return {
                criterion.codename: criterion(dsm)
                for criterion in self.criteria
            }
