# -*- coding: utf-8 -*-

"""
Archan package.

The purpose of this package is to make possible the analysis of a problem
using a DSM (Design Structure Matrix) on which certain criteria will be
verified.
"""

from .dsm import DesignStructureMatrix
from .errors import DSMError
from .analyzers import Analyzer
from .providers import Provider, CSVFileProvider
from .checkers import (
    Checker, CodeClean, CompleteMediation, LeastCommonMechanism,
    EconomyOfMechanism, LayeredArchitecture, LeastPrivileges,
    SeparationOfPrivileges, OpenDesign)
from .utils import Argument

__version__ = '1.0.0'
