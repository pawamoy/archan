"""Archan package.

The purpose of this package is to make possible the analysis of a problem
using a DSM (Design Structure Matrix) on which certain criteria will be
verified.
"""

from __future__ import annotations

from archan.dsm import DesignStructureMatrix, DomainMappingMatrix, MultipleDomainMatrix
from archan.logging import Logger
from archan.plugins import Argument, Checker, Provider

__all__: list[str] = [
    "DesignStructureMatrix",
    "DomainMappingMatrix",
    "MultipleDomainMatrix",
    "Provider",
    "Checker",
    "Argument",
    "Logger",
]

# TODO: DSM class should have more methods (see wiki DSM, adjacency matrix)
# FIXME: use if not sys.stdin.isatty() to detect stdin input or not
# TODO: update docs with new ignore param on all checkers
# TODO: update docs with new identifier class attributes on every plugin
# TODO: update docs with usage of self.logger in plugins
# TODO: update docs with new YAML format: identifier, name and description
# FIXME: stronger verification method for configuration
