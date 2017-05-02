# -*- coding: utf-8 -*-

# Copyright (c) 2015 Pierre Parrend
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Checker module.

Contains the Archan class.
"""

from __future__ import absolute_import, unicode_literals

from .criterion import CRITERIA, Criterion


class Archan(object):
    """Architecture analyser class."""

    def __init__(self, criteria=None):
        """
        Init method.

        Args:
            criteria (list): list of criteria to attach. These are the
                default criteria that will be checked when running check
                command without a criteria argument.
        """
        if criteria is None:
            criteria = CRITERIA
        self.criteria = criteria

    def check(self, dsm, criteria=None):
        """
        Check given criteria on given DSM.

        Args:
            dsm (:class:`DesignStructureMatrix`): the DSM to check.
            criteria (list): the list of criteria to check for.

        Returns:
            dict: {criterion codename:
                   Criterion.FAILED, PASSED, NOT_IMPLEMENTED or IGNORED}
        """
        if criteria:
            return {
                criterion.codename:
                    criterion(dsm)
                    if criterion in criteria
                    else (Criterion.IGNORED, '')
                for criterion in self.criteria
            }
        return {
            criterion.codename: criterion(dsm)
            for criterion in self.criteria
        }
