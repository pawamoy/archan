# -*- coding: utf-8 -*-

"""Configuration module."""

import collections
import importlib
import os
import pkg_resources
import yaml

from colorama import Fore, Style

from .analyzers import Analyzer
from .checkers import Checker
from .errors import ConfigError
from .providers import Provider
from .utils import console_width


class Config(object):
    def __init__(self, config_dict=None):
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
    def default_config():
        return Config()

    @staticmethod
    def print_result(result):
        print('%s %s' % ('{}'.format(result['checker'].name + ':'), {
            Checker.NOT_IMPLEMENTED: '{}not implemented{}'.format(
                Fore.YELLOW, Style.RESET_ALL),
            Checker.IGNORED: 'ignored',
            Checker.FAILED: '{}failed{}'.format(
                Fore.RED, Style.RESET_ALL),
            Checker.PASSED: '{}passed{}'.format(
                Fore.GREEN, Style.RESET_ALL),
        }.get(result['result'][0])))
        if result['result'][1]:
            print('  ' + result['result'][1])
            if result['checker'].hint:
                print('  Hint: ' + result['checker'].hint)

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
            if result['result'][0] == Checker.FAILED:
                return False
        return True

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
            return Config.load_local_plugin(name)
        except ImportError:
            return None

    def get_analyzer(self, name):
        return self.get_plugin(name, cls='analyzer')

    def get_provider(self, name):
        return self.get_plugin(name, cls='provider')

    def get_checker(self, name):
        return self.get_plugin(name, cls='checker')

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
                    # TODO: warn
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
                    # TODO: warn
                    checker = None
                if checker is not None:
                    real_checkers.append(checker)

        return Analyzer(providers=real_providers, checkers=real_checkers)

    def provider_from_dict(self, d):
        provider_name = list(d.keys())[0]
        provider_class = self.get_provider(provider_name)
        provider = provider_class(**d[provider_name])
        return provider

    def checker_from_dict(self, d):
        checker_name = list(d.keys())[0]
        checker_class = self.get_checker(checker_name)
        checker = checker_class(**d[checker_name])
        return checker

    def run(self):
        results = []
        for analyzer in self.analyzers:
            results.extend(analyzer.collect_results())
        self.results = results

    def print_results(self):
        for result in self.results:
            Config.print_result(result)

    def print_plugins(self):
        line = Fore.MAGENTA + Style.BRIGHT + '-' * console_width()
        if self.available_analyzers:
            print(line + '\nAnalyzers\n' + line)
            for analyzer in sorted(self.available_analyzers.values(),
                                   key=lambda x: x.name):
                print(analyzer.get_help())
        if self.available_providers:
            print(line + '\nProviders\n' + line)
            for provider in sorted(self.available_providers.values(),
                                   key=lambda x: x.name):
                print(provider.get_help())
        if self.available_checkers:
            print(line + '\nCheckers\n' + line)
            for checker in sorted(self.available_checkers.values(),
                                  key=lambda x: x.name):
                print(checker.get_help())
