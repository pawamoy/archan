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


# TODO: DSM class should have more methods (see wiki DSM, adjacency matrix)
# FIXME: use if not sys.stdin.isatty() to detect stdin input or not
# TODO: update docs with new ignore param on all checkers
# TODO: update docs with new identifier class attributes on every plugin
# TODO: update docs with usage of self.logger in plugins
# TODO: update docs with new YAML format: identifier, name and description
# FIXME: stronger verification method for configuration

