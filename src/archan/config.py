# -*- coding: utf-8 -*-

"""Configuration module."""

import collections
import importlib
import os
import sys

import pkg_resources
import yaml
from colorama import Style

from .analysis import AnalysisGroup
from .plugins import Checker, Provider
from .plugins.printing import console_width
from .errors import ConfigError
from .logging import Logger


logger = Logger.get_logger(__name__)


class Config(object):
    """Configuration class."""

    def __init__(self, config_dict=None):
        """
        Initialization method.

        Args:
            config_dict (dict): the configuration as a dictionary.
        """
        self.config_dict = config_dict
        self.plugins = Config.load_installed_plugins()
        self.analysis_groups = []

        if not config_dict:
            return

        analysis = config_dict['analysis']

        if isinstance(analysis, dict):

            for group_key, group_def in analysis.items():

                current_group = AnalysisGroup()

                if isinstance(group_key, str):

                    if isinstance(group_def, dict):
                        try:
                            plugin = self.get_plugin(group_key)
                            plugin = plugin(run_kwargs=group_def.get('arguments'))
                            if isinstance(plugin, Checker):
                                plugin.allow_failure = group_def.get('allow_failure', False)
                                if 'providers' not in group_def:
                                    raise ValueError

                            elif isinstance(plugin, Provider):
                                if 'checkers' not in group_def:
                                    raise ValueError

                        except ImportError:
                            logger.warning(
                                'Could not find any plugin identified by %s, '
                                'considering entry as group name.', group_key)
                            for value_key, value_value in group_def.items():
                                checker = Checker()
                                if isinstance(value_value, bool):
                                    checker.pass_ = value_value
                                elif isinstance(value_value, dict):
                                    checker.pass_ = value_value.get('pass', False)
                                    checker.pass_ = value_value.get('allow_failure', False)
                                else:
                                    raise NotImplementedError
                                current_group.checkers.append(checker)
                    else:
                        raise ValueError

                else:
                    raise NotImplementedError(
                        'Other types than str are not yet supported')

                self.analysis_groups.append(current_group)

        elif isinstance(analysis, (list, tuple, set)):

            for item in analysis:

                if isinstance(item, str):

                elif isinstance(item, dict):

                else:
                    raise NotImplementedError(
                        'Other types than str and dict are not yet supported')

        else:

            raise ValueError

        # 1P 1C
        # 1C 1P
        # 1P NC
        # 1C NP
        # no data

    def __str__(self):
        return str(self.config_dict)

    @staticmethod
    def load_local_plugin(name):
        """Import a local plugin accessible through Python path."""
        module_name = '.'.join(name.split('.')[:-1])
        module_obj = importlib.import_module(name=module_name)
        obj = getattr(module_obj, name.split('.')[-1])
        return obj

    @staticmethod
    def load_installed_plugins():
        """Search and load every installed plugin through entry points."""
        providers = {}
        checkers = {}
        for entry_point in pkg_resources.iter_entry_points(group='archan'):
            obj = entry_point.load()
            if issubclass(obj, Provider):
                providers[entry_point.name] = obj
            elif issubclass(obj, Checker):
                checkers[entry_point.name] = obj
        return collections.namedtuple(
            'Plugins', 'providers checkers')(
                providers=providers,
                checkers=checkers)

    @staticmethod
    def lint(config):
        """Verify the contents of the configuration dictionary."""
        if not isinstance(config, dict):
            raise ConfigError('config must be a dict')
        if 'analysis' not in config:
            raise ConfigError('config must have "analysis" item')

    @staticmethod
    def from_file(path):
        """Return a ``Config`` instance by reading a configuration file."""
        with open(path) as stream:
            obj = yaml.safe_load(stream)
        Config.lint(obj)
        return Config(config_dict=obj)

    @staticmethod
    def find():
        """Find the configuration file if any."""
        names = ('archan.yml', 'archan.yaml', '.archan.yml', '.archan.yaml')
        current_dir = os.getcwd()
        configconfig_file = os.path.join(current_dir, '.configconfig')
        default_config_dir = os.path.join(current_dir, 'config')
        if os.path.isfile(configconfig_file):
            logger.debug('Reading %s to get config folder path', configconfig_file)
            with open(configconfig_file) as stream:
                config_dir = os.path.join(current_dir, stream.read()).strip()
        elif os.path.isdir(default_config_dir):
            config_dir = default_config_dir
        else:
            config_dir = current_dir
        logger.debug('Config folder = %s', config_dir)
        for name in names:
            config_file = os.path.join(config_dir, name)
            logger.debug('Searching for config file at %s', config_file)
            if os.path.isfile(config_file):
                logger.debug('Found %s', config_file)
                return config_file
        logger.debug('No config file found')
        return None

    @staticmethod
    def default_config(file_path=sys.stdin):
        """Return a default configuration instance."""
        return Config({
            'analysis': {
                'archan.CSVInput': {
                    'arguments': {
                        'file_path': file_path
                    },
                    'checkers': (
                        'archan.CompleteMediation',
                        'archan.EconomyOfMechanism',
                        'archan.LeastCommonMechanism',
                        'archan.LayeredArchitecture'
                    )
                }
            }
        })

    @property
    def available_providers(self):
        """Return the available providers."""
        return self.plugins.providers

    @property
    def available_checkers(self):
        """Return the available checkers."""
        return self.plugins.checkers

    def get_plugin(self, identifier, cls=None):
        """
        Return the plugin corresponding to the given identifier and type.

        Args:
            identifier (str): identifier of the plugin.
            cls (str): one of checker / provider.

        Returns:
            Checker/Provider: plugin class.
        """
        if (cls is None or cls == 'provider') and identifier in self.available_providers:
            return self.available_providers[identifier]
        elif (cls is None or cls == 'checker') and identifier in self.available_checkers:
            return self.available_checkers[identifier]
        return Config.load_local_plugin(identifier)


    def get_provider(self, identifier):
        """Return the provider class corresponding to the given identifier."""
        return self.get_plugin(identifier, cls='provider')

    def get_checker(self, identifier):
        """Return the checker class corresponding to the given identifier."""
        return self.get_plugin(identifier, cls='checker')

    def provider_from_dict(self, dct):
        """Return a provider instance from a dict object."""
        provider_identifier = list(dct.keys())[0]
        provider_class = self.get_provider(provider_identifier)
        if provider_class:
            return provider_class(**dct[provider_identifier])
        return None

    def checker_from_dict(self, dct):
        """Return a checker instance from a dict object."""
        checker_identifier = list(dct.keys())[0]
        checker_class = self.get_checker(checker_identifier)
        if checker_class:
            return checker_class(**dct[checker_identifier])
        return None

    def print_plugins(self):
        """Print the available plugins."""
        width = console_width()
        line = Style.BRIGHT + '=' * width + '\n'
        middle = int(width / 2)
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



    def inflate_provider(self, identifier, definition=None):
        return self.inflate_plugin(identifier, definition, 'provider')

    def inflate_providers(self, provider_list):
        return self.inflate_plugins(provider_list, self.inflate_provider)

    def inflate_checker(self, identifier, definition=None):
        return self.inflate_plugin(identifier, definition, 'checker')

    def inflate_checkers(self, checker_list):
        return self.inflate_plugins(checker_list, self.inflate_checker)

    def inflate_plugin(self, identifier, definition=None, cls=None):
        cls = self.get_plugin(identifier, cls)
        return cls(**definition or {})

    @staticmethod
    def inflate_plugins(plugin_list, inflate_plugin):
        plugins = []
        for plugin_def in plugin_list:
            if isinstance(plugin_def, str):
                plugins.append(inflate_plugin(plugin_def))
            elif isinstance(plugin_def, dict):
                if len(plugin_def) > 1:
                    raise ValueError(
                        'When using a plugin list, each dictionary item '
                        'must contain only one key.')
                identifier = list(plugin_def.keys())[0]
                definition = plugin_def[identifier]
                plugins.append(inflate_plugin(identifier, definition))
        return plugins

    def inflate_analysis_group(self, identifier, definition):
        analysis_group = AnalysisGroup()
        providers_definition = definition.pop('providers')
        checkers_definition = definition.pop('checkers')

        try:
            first_plugin = self.inflate_plugin(identifier, definition)

            if isinstance(first_plugin, Checker):
                analysis_group.checkers.append(first_plugin)

                if providers_definition is None:
                    raise ValueError

                if isinstance(providers_definition, list):
                    analysis_group.providers.extend(self.inflate_providers(providers_definition))
                elif isinstance(providers_definition, dict):
                    analysis_group.providers.extend(self.inflate_providers(providers_definition))
                else:
                    raise ValueError

            elif isinstance(first_plugin, Provider):
                analysis_group.providers.append(first_plugin)

                if checkers_definition is None:
                    raise ValueError

                if isinstance(checkers_definition, list):
                    analysis_group.checkers.extend(self.inflate_providers(checkers_definition))
                elif isinstance(checkers_definition, dict):
                    analysis_group.checkers.extend(self.inflate_providers(checkers_definition))
                else:
                    raise ValueError

        except ImportError:
            logger.warning(
                'Could not find any plugin identified by %s, '
                'considering entry as group name.', identifier)
            for value_key, value_value in definition.items():
                checker = Checker()
                if isinstance(value_value, bool):
                    checker.pass_ = value_value
                elif isinstance(value_value, dict):
                    checker.pass_ = value_value.get('pass', False)
                    checker.pass_ = value_value.get('allow_failure', False)
                else:
                    raise NotImplementedError
                current_group.checkers.append(checker)
