# -*- coding: utf-8 -*-

"""Configuration module."""

import collections
import importlib
import os
import sys

import pkg_resources
import yaml
from colorama import Style
from copy import deepcopy

from .analysis import AnalysisGroup
from .plugins import Checker, Provider
from .plugins.printing import console_width
from .errors import ConfigError
from .logging import Logger


try:
    ModuleNotFoundError = ModuleNotFoundError
except NameError:
    ModuleNotFoundError = ImportError

logger = Logger.get_logger(__name__)


class Config(object):
    """Configuration class."""

    def __init__(self, config_dict=None):
        """
        Initialization method.

        Args:
            config_dict (dict): the configuration as a dictionary.
        """
        self.config_dict = deepcopy(config_dict)
        self.plugins = Config.load_installed_plugins()
        self.analysis_groups = []

        if not config_dict:
            return

        analysis = config_dict.get('analysis', {})

        if isinstance(analysis, dict):
            for group_key, group_def in analysis.items():
                self.analysis_groups.append(self.inflate_analysis_group(group_key, group_def))
        else:
            raise ValueError

    def __str__(self):
        return str(self.config_dict)

    @staticmethod
    def load_local_plugin(name):
        """Import a local plugin accessible through Python path."""
        try:
            module_name = '.'.join(name.split('.')[:-1])
            module_obj = importlib.import_module(name=module_name)
            obj = getattr(module_obj, name.split('.')[-1])
            return obj
        except (ImportError, AttributeError, ModuleNotFoundError, ValueError):
            raise ModuleNotFoundError

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

    @staticmethod
    def inflate_plugin_list(plugin_list, inflate_plugin):
        plugins = []
        for plugin_def in plugin_list:
            if isinstance(plugin_def, str):
                try:
                    plugins.append(inflate_plugin(plugin_def))
                except ModuleNotFoundError:
                    logger.error('Could not import plugin identified by %s.', plugin_def)
            elif isinstance(plugin_def, dict):
                if len(plugin_def) > 1:
                    raise ValueError(
                        'When using a plugin list, each dictionary item '
                        'must contain only one key.')
                identifier = list(plugin_def.keys())[0]
                definition = plugin_def[identifier]
                try:
                    plugins.append(inflate_plugin(identifier, definition))
                except ModuleNotFoundError:
                    logger.error('Could not import plugin identified by %s. '
                                 'Inflate method: %s', identifier, inflate_plugin)
        return plugins

    @staticmethod
    def inflate_plugin_dict(plugin_dict, inflate_plugin):
        plugins = []
        for identifier, definition in plugin_dict.items():
            try:
                plugins.append(inflate_plugin(identifier, definition))
            except ModuleNotFoundError:
                logger.error('Could not import plugin identified by %s.', identifier)
        return plugins

    @staticmethod
    def inflate_nd_checker(identifier, definition):
        if isinstance(definition, bool):
            return Checker(name=identifier, passes=definition)
        elif isinstance(definition, dict):
            return Checker(definition.pop('name', identifier), **definition)
        else:
            raise ValueError

    @staticmethod
    def cleanup_definition(definition):
        definition.pop('name', '')
        definition.pop('description', '')
        definition.pop('arguments', '')

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

    def inflate_plugin(self, identifier, definition=None, cls=None):
        cls = self.get_plugin(identifier, cls)
        return cls(**definition or {})

    def inflate_plugins(self, plugins_definition, inflate_method):
        if isinstance(plugins_definition, list):
            return self.inflate_plugin_list(plugins_definition, inflate_method)
        elif isinstance(plugins_definition, dict):
            return self.inflate_plugin_dict(plugins_definition, inflate_method)
        else:
            raise ValueError

    def inflate_provider(self, identifier, definition=None):
        return self.inflate_plugin(identifier, definition, 'provider')

    def inflate_checker(self, identifier, definition=None):
        return self.inflate_plugin(identifier, definition, 'checker')

    def inflate_providers(self, providers_definition):
        return self.inflate_plugins(providers_definition, self.inflate_provider)

    def inflate_checkers(self, checkers_definition):
        return self.inflate_plugins(checkers_definition, self.inflate_checker)

    def inflate_analysis_group(self, identifier, definition):
        providers_definition = definition.pop('providers', None)
        checkers_definition = definition.pop('checkers', None)

        analysis_group = AnalysisGroup()

        try:

            first_plugin = self.inflate_plugin(identifier, definition)

            analysis_group.name = first_plugin.name
            analysis_group.description = first_plugin.description

            if isinstance(first_plugin, Checker):
                analysis_group.checkers.append(first_plugin)

                if providers_definition is None:
                    raise ValueError

                analysis_group.providers.extend(self.inflate_providers(providers_definition))

            elif isinstance(first_plugin, Provider):
                analysis_group.providers.append(first_plugin)

                if checkers_definition is None:
                    raise ValueError

                analysis_group.checkers.extend(self.inflate_checkers(checkers_definition))

        except ModuleNotFoundError:

            logger.warning(
                'Could not find any plugin identified by %s, '
                'considering entry as group name.', identifier)

            analysis_group.name = definition.pop('name', identifier)
            analysis_group.description = definition.pop('description', None)

            if providers_definition:
                analysis_group.providers.extend(self.inflate_providers(providers_definition))

            if checkers_definition:
                analysis_group.checkers.extend(self.inflate_checkers(checkers_definition))

        self.cleanup_definition(definition)

        for nd_identifier, nd_definition in definition.items():
            analysis_group.checkers.append(self.inflate_nd_checker(nd_identifier, nd_definition))

        return analysis_group
