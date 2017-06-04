# -*- coding: utf-8 -*-

"""
Checker module.

Contains the ``Archan`` class.
"""

from collections import OrderedDict

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
        result = OrderedDict()
        if criteria:
            for criterion in self.criteria:
                if criterion in criteria:
                    result[criterion] = criterion(dsm)
                else:
                    result[criterion] = (Criterion.IGNORED, '')
        else:
            for criterion in self.criteria:
                result[criterion] = criterion(dsm)
        return result
