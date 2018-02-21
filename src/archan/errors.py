# -*- coding: utf-8 -*-

"""Errors module."""


class MatrixError(Exception):
    """Exception raised when matrix data are incorrect."""


class DesignStructureMatrixError(MatrixError):
    """DesignStructureMatrix-specific matrix error."""


class DomainMappingMatrixError(MatrixError):
    """DomainMappingMatrix-specific matrix error."""


class MultipleDomainMatrixError(MatrixError):
    """MultipleDomainMatrix-specific matrix error."""


class ConfigError(Exception):
    """Exception raised for errors in the configuration."""
