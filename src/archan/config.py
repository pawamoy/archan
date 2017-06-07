# -*- coding: utf-8 -*-

"""Configuration module."""

import collections
import importlib
import os
import pkg_resources
import sys
import yaml

from colorama import Style

from .analyzers import Analyzer, DefaultAnalyzer
from .checkers import Checker
from .errors import ConfigError
from .providers import Provider, CSVInput
from .utils import console_width, Logger


class Config(object):
    def __init__(self, config_dict=None):
        self.logger = Logger.get_logger(__name__)
        self.plugins = Config.load_installed_plugins()
        self.analyzers = []

        if config_dict is None:
            return

        analyzers = config_dict['analyzers']
        for analyzer in analyzers:
            if isinstance(analyzer, str):
                analyzer = self.get_analyzer(analyzer)
            elif isinstance(analyzer, dict):
                analyzer = self.analyzer_from_dict(analyzer)
            elif isinstance(analyzer, Analyzer):
                pass
            elif issubclass(analyzer, Analyzer):
                analyzer = analyzer()
            else:
                # TODO: warn
                analyzer = None
            if analyzer is not None:
                self.analyzers.append(analyzer)

        self.results = []

    @staticmethod
    def load_local_plugin(name):
        module_name = '.'.join(name.split('.')[:-1])
        module_obj = importlib.import_module(name=module_name)
        obj = getattr(module_obj, name.split('.')[-1])
        return obj

    @staticmethod
    def load_installed_plugins():
        analyzers = {}
        providers = {}
        checkers = {}
        for ep in pkg_resources.iter_entry_points(group='archan'):
            obj = ep.load()
            if issubclass(obj, Analyzer):
                analyzers[ep.name] = obj
            elif issubclass(obj, Provider):
                providers[ep.name] = obj
            elif issubclass(obj, Checker):
                checkers[ep.name] = obj
        return collections.namedtuple(
            'Plugins', 'analyzers providers checkers')(
                analyzers=analyzers,
                providers=providers,
                checkers=checkers)

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

    @staticmethod
    def find():
        names = ('archan.yml', 'archan.yaml', '.archan.yml', '.archan.yaml')
        current_dir = os.getcwd()
        configconfig_file = os.path.join(current_dir, '.configconfig')
        default_config_dir = os.path.join(current_dir, 'config')
        if os.path.isfile(configconfig_file):
            with open(configconfig_file) as f:
                config_dir = os.path.join(current_dir, f.read()).strip()
        elif os.path.isdir(default_config_dir):
            config_dir = default_config_dir
        else:
            config_dir = current_dir
        for name in names:
            config_file = os.path.join(config_dir, name)
            if os.path.isfile(config_file):
                return config_file
        return None

    @staticmethod
    def default_config(file_path=sys.stdin):
        return Config(dict(analyzers=[DefaultAnalyzer(
            providers=[CSVInput(file_path=file_path)])]))

    @property
    def available_analyzers(self):
        return self.plugins.analyzers

    @property
    def available_providers(self):
        return self.plugins.providers

    @property
    def available_checkers(self):
        return self.plugins.checkers

    @property
    def successful(self):
        for result in self.results:
            if result.code == Checker.FAILED:
                return False
        return True

    def get_plugin(self, identifier, cls=None):
        if cls:
            search_in = {}
            if cls == 'analyzer':
                search_in = self.available_analyzers
            elif cls == 'provider':
                search_in = self.available_providers
            elif cls == 'checker':
                search_in = self.available_checkers
            if identifier in search_in:
                return search_in[identifier]
        try:
            return Config.load_local_plugin(identifier)
        except ImportError:
            self.logger.warning('Plugin %s is not importable' % identifier)
            return None

    def get_analyzer(self, identifier):
        return self.get_plugin(identifier, cls='analyzer')

    def get_provider(self, identifier):
        return self.get_plugin(identifier, cls='provider')

    def get_checker(self, identifier):
        return self.get_plugin(identifier, cls='checker')

    def analyzer_from_dict(self, d):
        providers = d['providers']
        checkers = d['checkers']
        real_providers = []
        real_checkers = []

        if isinstance(providers, str):
            real_providers = [self.get_provider(providers)]
        elif isinstance(providers, list):
            for provider in providers:
                if isinstance(provider, str):
                    provider = self.get_provider(provider)()
                elif isinstance(provider, dict):
                    provider = self.provider_from_dict(provider)
                elif isinstance(provider, provider):
                    pass
                elif issubclass(provider, provider):
                    provider = provider()
                else:
                    provider = None
                if provider is not None:
                    real_providers.append(provider)

        if isinstance(checkers, str):
            real_checkers = [self.get_checker(checkers)]
        elif isinstance(checkers, list):
            for checker in checkers:
                if isinstance(checker, str):
                    checker = self.get_checker(checker)()
                elif isinstance(checker, dict):
                    checker = self.checker_from_dict(checker)
                elif isinstance(checker, Checker):
                    pass
                elif issubclass(checker, Checker):
                    checker = checker()
                else:
                    checker = None
                if checker is not None:
                    real_checkers.append(checker)

        return Analyzer(
            identifier=d.get('identifier', None),
            name=d.get('name', None), description=d.get('description', None),
            providers=real_providers, checkers=real_checkers)

    def provider_from_dict(self, d):
        provider_identifier = list(d.keys())[0]
        provider_class = self.get_provider(provider_identifier)
        if provider_class:
            return provider_class(**d[provider_identifier])
        return None

    def checker_from_dict(self, d):
        checker_identifier = list(d.keys())[0]
        checker_class = self.get_checker(checker_identifier)
        if checker_class:
            return checker_class(**d[checker_identifier])
        return None

    def run(self):
        results = []
        for analyzer in self.analyzers:
            results.extend(analyzer.collect_results())
        self.results = results

    def print_results(self):
        one_analyzer = len(self.analyzers) == 1
        for result in self.results:
            one_provider = len(result.analyzer.providers) == 1
            result.print(analyzer=not one_analyzer, provider=not one_provider)

    def print_plugins(self):
        width = console_width()
        line = Style.BRIGHT + '=' * width + '\n'
        middle = int(width / 2)
        if self.available_analyzers:
            print(line + ' ' * middle + 'ANALYZERS')
            for analyzer in sorted(self.available_analyzers.values(),
                                   key=lambda x: x.identifier):
                print(analyzer.get_help())
        if self.available_providers:
            print(line + ' ' * middle + 'PROVIDERS')
            for provider in sorted(self.available_providers.values(),
                                   key=lambda x: x.identifier):
                print(provider.get_help())
        if self.available_checkers:
            print(line + ' ' * middle + 'CHECKERS')
            for checker in sorted(self.available_checkers.values(),
                                  key=lambda x: x.identifier):
                print(checker.get_help())
