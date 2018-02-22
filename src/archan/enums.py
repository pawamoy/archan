# -*- coding: utf-8 -*-

"""Enumerations module."""


class MetaEnum(type):
    ALL = ()

    def __contains__(cls, item):
        return item in cls.ALL


class ResultCode(metaclass=MetaEnum):
    PASSED = 1
    FAILED = 0
    IGNORED = -1
    NOT_IMPLEMENTED = -2

    ALL = (PASSED, FAILED, IGNORED, NOT_IMPLEMENTED)
