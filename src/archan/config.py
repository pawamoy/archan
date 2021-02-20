# -*- coding: utf-8 -*-

"""Configuration module."""

import collections
import importlib
import os
import sys
from copy import deepcopy

import pkg_resources
import yaml
from colorama import Style

from .analysis import AnalysisGroup
from .errors import ConfigError
from .logging import Logger
from .plugins import Checker, Provider
from .printing import console_width

try:

    class PluginNotFoundError(ModuleNotFoundError):
        """Exception to raise when a plugin is not found or importable."""


except NameError:

    class PluginNotFoundError(ImportError):  # type: ignore
        """Exception to raise when a plugin is not found or importable."""


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

        analysis = config_dict.get("analysis", {})

        if isinstance(analysis, dict):
            for group_key, group_def in analysis.items():
                try:
                    self.analysis_groups.append(self.inflate_analysis_group(group_key, group_def))
                except ValueError as e:
                    logger.error(
                        'Error while inflating "%s" analysis group. '
                        "The group will not be added to the list. "
                        "Exception: %s.",
                        group_key,
                        e,
                    )
        else:
            raise ValueError('%s type is not supported for "analysis" key, ' "use dict only" % type(analysis))

    def __str__(self):
        return str(self.config_dict)

    @staticmethod
    def load_local_plugin(name):
        """Import a local plugin accessible through Python path."""
        try:
            module_name = ".".join(name.split(".")[:-1])
            module_obj = importlib.import_module(name=module_name)
            obj = getattr(module_obj, name.split(".")[-1])
            return obj
        except (ImportError, AttributeError, ValueError) as e:
            raise PluginNotFoundError(e)

    @staticmethod
    def load_installed_plugins():
        """Search and load every installed plugin through entry points."""
        providers = {}
        checkers = {}
        for entry_point in pkg_resources.iter_entry_points(group="archan"):
            obj = entry_point.load()
            if issubclass(obj, Provider):
                providers[entry_point.name] = obj
            elif issubclass(obj, Checker):
                checkers[entry_point.name] = obj
        return collections.namedtuple("Plugins", "providers checkers")(providers=providers, checkers=checkers)

    @staticmethod
    def lint(config):
        """Verify the contents of the configuration dictionary."""
        if not isinstance(config, dict):
            raise ConfigError("config must be a dict")
        if "analysis" not in config:
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
        names = ("archan.yml", "archan.yaml", ".archan.yml", ".archan.yaml")
        current_dir = os.getcwd()
        configconfig_file = os.path.join(current_dir, ".configconfig")
        default_config_dir = os.path.join(current_dir, "config")
        if os.path.isfile(configconfig_file):
            logger.debug("Reading %s to get config folder path", configconfig_file)
            with open(configconfig_file) as stream:
                config_dir = os.path.join(current_dir, stream.read()).strip()
        elif os.path.isdir(default_config_dir):
            config_dir = default_config_dir
        else:
            config_dir = current_dir
        logger.debug("Config folder = %s", config_dir)
        for name in names:
            config_file = os.path.join(config_dir, name)
            logger.debug("Searching for config file at %s", config_file)
            if os.path.isfile(config_file):
                logger.debug("Found %s", config_file)
                return config_file
        logger.debug("No config file found")
        return None

    @staticmethod
    def default_config(file_path=None):
        """Return a default configuration instance."""
        return Config(
            {
                "analysis": {
                    "archan.CSVInput": {
                        "arguments": {"file_path": file_path},
                        "checkers": (
                            "archan.CompleteMediation",
                            "archan.EconomyOfMechanism",
                            "archan.LeastCommonMechanism",
                            "archan.LayeredArchitecture",
                        ),
                    }
                }
            }
        )

    @staticmethod
    def inflate_plugin_list(plugin_list, inflate_plugin):
        """
        Inflate a list of strings/dictionaries to a list of plugin instances.

        Args:
            plugin_list (list): a list of str/dict.
            inflate_plugin (method): the method to inflate the plugin.

        Returns:
            list: a plugin instances list.

        Raises:
            ValueError: when a dictionary item contains more than one key.
        """
        plugins = []
        for plugin_def in plugin_list:
            if isinstance(plugin_def, str):
                try:
                    plugins.append(inflate_plugin(plugin_def))
                except PluginNotFoundError as e:
                    logger.error("Could not import plugin identified by %s. " "Exception: %s.", plugin_def, e)
            elif isinstance(plugin_def, dict):
                if len(plugin_def) > 1:
                    raise ValueError("When using a plugin list, each dictionary item " "must contain only one key.")
                identifier = list(plugin_def.keys())[0]
                definition = plugin_def[identifier]
                try:
                    plugins.append(inflate_plugin(identifier, definition))
                except PluginNotFoundError as e:
                    logger.error(
                        "Could not import plugin identified by %s. " "Inflate method: %s. Exception: %s.",
                        identifier,
                        inflate_plugin,
                        e,
                    )
        return plugins

    @staticmethod
    def inflate_plugin_dict(plugin_dict, inflate_plugin):
        """
        Inflate a list of strings/dictionaries to a list of plugin instances.

        Args:
            plugin_dict (dict): a dict of dict.
            inflate_plugin (method): the method to inflate the plugin.

        Returns:
            list: a plugin instances list.
        """
        plugins = []
        for identifier, definition in plugin_dict.items():
            try:
                plugins.append(inflate_plugin(identifier, definition))
            except PluginNotFoundError as e:
                logger.error("Could not import plugin identified by %s. " "Exception: %s.", identifier, e)
        return plugins

    @staticmethod
    def inflate_nd_checker(identifier, definition):
        """
        Inflate a no-data checker from a basic definition.

        Args:
            identifier (str): the no-data checker identifier / name.
            definition (bool/dict): a boolean acting as "passes" or a full
                dict definition with "passes" and "allow_failure".

        Returns:
            Checker: a checker instance.

        Raises:
            ValueError: when the definition type is not bool or dict.
        """
        if isinstance(definition, bool):
            return Checker(name=identifier, passes=definition)
        elif isinstance(definition, dict):
            return Checker(definition.pop("name", identifier), **definition)
        else:
            raise ValueError("%s type is not supported for no-data checkers, " "use bool or dict" % type(definition))

    @staticmethod
    def cleanup_definition(definition):
        """Clean-up a definition (remove name, description and arguments)."""
        definition.pop("name", "")
        definition.pop("description", "")
        definition.pop("arguments", "")

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
        if (cls is None or cls == "provider") and identifier in self.available_providers:
            return self.available_providers[identifier]
        elif (cls is None or cls == "checker") and identifier in self.available_checkers:
            return self.available_checkers[identifier]
        return Config.load_local_plugin(identifier)

    def get_provider(self, identifier):
        """Return the provider class corresponding to the given identifier."""
        return self.get_plugin(identifier, cls="provider")

    def get_checker(self, identifier):
        """Return the checker class corresponding to the given identifier."""
        return self.get_plugin(identifier, cls="checker")

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

    def inflate_plugin(self, identifier, definition=None, cls=None):
        """
        Inflate a plugin thanks to it's identifier, definition and class.

        Args:
            identifier (str): the plugin identifier.
            definition (dict): the kwargs to instantiate the plugin with.
            cls (str): "provider", "checker", or None.

        Returns:
            Provider/Checker: instance of plugin.
        """
        cls = self.get_plugin(identifier, cls)
        # TODO: implement re-usability of plugins?
        # same instances shared across analyses (to avoid re-computing stuff)
        return cls(**definition or {})

    def inflate_plugins(self, plugins_definition, inflate_method):
        """
        Inflate multiple plugins based on a list/dict definition.

        Args:
            plugins_definition (list/dict): the plugins definitions.
            inflate_method (method): the method to indlate each plugin.

        Returns:
            list: a list of plugin instances.

        Raises:
            ValueError: when the definition type is not list or dict.
        """
        if isinstance(plugins_definition, (list, tuple)):
            return self.inflate_plugin_list(plugins_definition, inflate_method)
        elif isinstance(plugins_definition, dict):
            return self.inflate_plugin_dict(plugins_definition, inflate_method)
        else:
            raise ValueError(
                "%s type is not supported for a plugin list, " "use list or dict" % type(plugins_definition)
            )

    def inflate_provider(self, identifier, definition=None):
        """Shortcut to inflate a provider."""
        return self.inflate_plugin(identifier, definition, "provider")

    def inflate_checker(self, identifier, definition=None):
        """Shortcut to inflate a checker."""
        return self.inflate_plugin(identifier, definition, "checker")

    def inflate_providers(self, providers_definition):
        """Shortcut to inflate multiple providers."""
        return self.inflate_plugins(providers_definition, self.inflate_provider)  # noqa

    def inflate_checkers(self, checkers_definition):
        """Shortcut to inflate multiple checkers."""
        return self.inflate_plugins(checkers_definition, self.inflate_checker)

    def inflate_analysis_group(self, identifier, definition):
        """
        Inflate a whole analysis group.

        An analysis group is a section defined in the YAML file.

        Args:
            identifier (str): the group identifier.
            definition (list/dict): the group definition.

        Returns:
            AnalysisGroup: an instance of AnalysisGroup.

        Raises:
            ValueError: when identifier targets a plugin of a certain type,
                and the definition does not contain the entry for the
                other-type plugins (providers <-> checkers).
        """
        providers_definition = definition.pop("providers", None)
        checkers_definition = definition.pop("checkers", None)

        analysis_group = AnalysisGroup()

        try:

            first_plugin = self.inflate_plugin(identifier, definition)

            if isinstance(first_plugin, Checker):
                analysis_group.checkers.append(first_plugin)

                if providers_definition is None:
                    raise ValueError(
                        "when declaring an analysis group with a checker "
                        "identifier, you must also declare providers with "
                        'the "providers" key.'
                    )

                analysis_group.providers.extend(self.inflate_providers(providers_definition))

            elif isinstance(first_plugin, Provider):
                analysis_group.providers.append(first_plugin)

                if checkers_definition is None:
                    raise ValueError(
                        "when declaring an analysis group with a provider "
                        "identifier, you must also declare checkers with "
                        'the "checkers" key.'
                    )

                analysis_group.checkers.extend(self.inflate_checkers(checkers_definition))

        except PluginNotFoundError as e:

            logger.warning(
                "Could not find any plugin identified by %s, " "considering entry as group name. Exception: %s.",
                identifier,
                e,
            )

            analysis_group.name = definition.pop("name", identifier)
            analysis_group.description = definition.pop("description", None)

            if bool(providers_definition) != bool(checkers_definition):
                raise ValueError(
                    "when declaring an analysis group with a name, you must "
                    'either declare both "providers" and "checkers" or none.'
                )

            if providers_definition and checkers_definition:
                analysis_group.providers.extend(self.inflate_providers(providers_definition))
                analysis_group.checkers.extend(self.inflate_checkers(checkers_definition))

        self.cleanup_definition(definition)

        for nd_identifier, nd_definition in definition.items():
            analysis_group.checkers.append(self.inflate_nd_checker(nd_identifier, nd_definition))

        return analysis_group

    def print_plugins(self):
        """Print the available plugins."""
        width = console_width()
        line = Style.BRIGHT + "=" * width + "\n"
        middle = int(width / 2)
        if self.available_providers:
            print(line + " " * middle + "PROVIDERS")
            for provider in sorted(self.available_providers.values(), key=lambda x: x.identifier):
                provider().print()
                print()
        if self.available_checkers:
            print(line + " " * middle + "CHECKERS")
            for checker in sorted(self.available_checkers.values(), key=lambda x: x.identifier):
                checker().print()
                print()
