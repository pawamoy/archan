# -*- coding: utf-8 -*-

"""Configuration module."""

import collections
import importlib
import pkg_resources
import yaml


class ConfigError(Exception):
    pass


class Config(object):
    def __init__(self, config_dict=None):
        self.plugins = load_installed_plugins()

        analyzers = config_dict['analyzers']
        for analyzer in analyzers:
            if isinstance(analyzer, str):
                pass
            elif isinstance(analyzer, dict):
                pass
            elif isinstance(analyzer, list):
                pass
            elif isinstance(analyzer, Analyzer):
                pass

    @staticmethod
    def verify(config):
        if not isinstance(config, dict):
            raise ConfigError('config must be a dict')
        if 'analyzers' not in config:
            raise ConfigError('config must have "analyzers" item')

    @staticmethod
    def from_file(path):
        with open(path) as f:
            obj = yaml.safe_load(f)
        Config.verify(obj)
        return Config(config_dict=obj)

    @property
    def available_analyzers(self):
        return self.plugins.analyzers

    @property
    def available_providers(self):
        return self.plugins.providers

    @property
    def available_checkers(self):
        return self.plugins.checkers

    def get_plugin(self, name, cls=None):
        if cls:
            search_in = {}
            if cls == 'analyzer':
                search_in = self.available_analyzers
            elif cls == 'provider':
                search_in = self.available_providers
            elif cls == 'checker':
                search_in = self.available_checkers
            if name in search_in:
                return search_in[name]
        try:
            return load_local_plugin(name)
        except ImportError:
            return None

    def get_analyzer(self, name):
        return self.get_plugin(name, cls='analyzer')

    def get_provider(self, name):
        return self.get_plugin(name, cls='provider')

    def get_checker(self, name):
        return self.get_plugin(name, cls='checker')


class Analyzer(object):
    pass


class Provider(object):
    pass


class Checker(object):
    pass


def load_local_plugin(name):
    module_name = '.'.join(name.split('.')[:-1])
    module_obj = importlib.import_module(name=module_name)
    obj = getattr(module_obj, name.split('.')[-1])
    return obj


def load_installed_plugins():
    analyzers = {}
    providers = {}
    checkers = {}
    for ep in pkg_resources.iter_entry_points(group='archan'):
        obj = ep.load()
        if isinstance(obj, Analyzer):
            analyzers[ep.name] = obj
        elif isinstance(obj, Provider):
            providers[ep.name] = obj
        elif isinstance(obj, Checker):
            checkers[ep.name] = obj
    return collections.namedtuple('Plugins', 'analyzers providers checkers')(
        analyzers=analyzers,
        providers=providers,
        checkers=checkers
    )
