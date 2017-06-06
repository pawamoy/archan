# -*- coding: utf-8 -*-

"""
Archan package.

The purpose of this package is to make possible the analysis of a problem
using a DSM (Design Structure Matrix) on which certain criteria will be
verified.
"""

from .dsm import DSM
from .analyzers import Analyzer
from .providers import Provider
from .checkers import Checker
from .utils import Argument

__all__ = ('DSM', 'Analyzer', 'Provider', 'Checker', 'Argument')
__version__ = '1.0.0'


# TODO: checker result should be a class to simplify printing and stuff
# TODO: DSM class should have more methods to sort the data,
# fill the matrix with transitive dependencies, etc.
# TODO: add option on checker to "ignore" the result (fail in yellow)
# FIXME: use if not sys.stdin.isatty() to detect stdin input or not
