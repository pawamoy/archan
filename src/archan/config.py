# -*- coding: utf-8 -*-

"""Configuration module."""

import yaml


class Config(object):
    def __init__(self, raw_config=None, analyzers=None):
        pass

    @staticmethod
    def from_file(path):
        with open(path) as f:
            obj = yaml.safe_load(f)
        Config.verify(obj)
        return Config(raw_config=obj)
