"""Enumerations module."""

from __future__ import annotations

from typing import Any


class MetaEnum(type):
    """Metaclass for our ResultCode enum."""

    ALL = ()

    def __contains__(cls, item: Any):
        return item in cls.ALL


class ResultCode(metaclass=MetaEnum):
    """Enumeration of our result codes."""

    PASSED = 1
    FAILED = 0
    IGNORED = -1
    NOT_IMPLEMENTED = -2

    ALL = (PASSED, FAILED, IGNORED, NOT_IMPLEMENTED)
