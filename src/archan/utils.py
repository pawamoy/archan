# -*- coding: utf-8 -*-

"""Utils module."""


class Argument(object):
    def __init__(self, name, type, description=None, default=None):
        self.name = name
        self.type = type
        self.description = description
        self.default = default

    def __str__(self):
        return '  %s (%s, default %s): %s' % (
            self.name, self.type, self.default, self.description)
