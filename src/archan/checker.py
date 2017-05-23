# -*- coding: utf-8 -*-

"""
Checker module.

Contains the ``Archan`` class.
"""

from .criterion import CRITERIA, Criterion


class Archan(object):
    """Architecture analysis class."""

    def __init__(self, criteria=None):
        """
        Initialization method.

        Args:
            criteria (list): list of criteria to attach. These are the
                default criteria that will be checked when running check
                command without a criteria argument.
        """
        if criteria is None:
            criteria = CRITERIA
        self.criteria = criteria

    def check(self, dsm, *criteria):
        """
        Check given criteria on given DSM.

        Args:
            dsm (:class:`DesignStructureMatrix`): the DSM to check.
            criteria (list): the list of criteria to check for.

        Returns:
            dict:
                code names as keys, Criterion.FAILED, PASSED, NOT_IMPLEMENTED
                or IGNORED as values.
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
