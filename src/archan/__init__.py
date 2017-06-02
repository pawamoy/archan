# -*- coding: utf-8 -*-

"""
Archan package.

This Python package provides four modules:

- ``checker``, with Archan class
- ``criterion``, with Criterion class
- ``dsm``, with DesignStructureMatrix class
- ``errors``, for exceptions

The purpose of this package is to make possible the analysis of a problem
using a DSM (Design Structure Matrix) on which certain criteria will be
verified.
"""

from .checker import Archan
from .criterion import Criterion
from .dsm import DesignStructureMatrix
from .errors import ArchanError, DSMError

__all__ = ('Archan', 'Criterion', 'DesignStructureMatrix',
           'ArchanError', 'DSMError')
