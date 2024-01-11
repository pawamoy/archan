"""Configuration module."""

from __future__ import annotations

import importlib
import os
import sys
from copy import deepcopy
from importlib.metadata import entry_points
from typing import Callable

import yaml
from colorama import Style

from archan.analysis import AnalysisGroup
from archan.errors import ConfigError
from archan.logging import Logger
from archan.plugins import Checker, Provider
from archan.printing import console_width


class PluginNotFoundError(ModuleNotFoundError):
    """Exception to raise when a plugin is not found or importable."""


logger = Logger.get_logger(__name__)


class Plugins:
    """Simple class used to store providers and checkers."""

    def __init__(self, providers: dict[str, type[Provider]], checkers: dict[str, type[Checker]]):
        """Initialize the object.

        Parameters:
            providers: Some providers.
            checkers: Some checkers.
        """
        self.providers = providers
        self.checkers = checkers


class Config:
    """Configuration class."""

    def __init__(self, config_dict: dict | None = None):
        """Initialize the object.

        Parameters:
            config_dict: the configuration as a dictionary.

        Raises:
            ValueError: When a wrong type is given for the analysis key.
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
                except ValueError as error:
                    logger.error(
                        f"Error while inflating '{group_key}' analysis group. "
                        "The group will not be added to the list. "
                        f"Exception: {error}.",
                    )
        else:
            raise TypeError(f"{type(analysis)} type is not supported for 'analysis' key, use dict only")

    def __str__(self):
        return str(self.config_dict)

    @staticmethod
    def load_local_plugin(name: str) -> type[Checker | Provider]:
        """Import a local plugin accessible through Python path.

        Parameters:
            name: Dotted path to the plugin.

        Raises:
            PluginNotFoundError: When the given plugin could not be found.

        Returns:
            The plugin object.
        """
        module_name = ".".join(name.split(".")[:-1])
        try:
            module_obj = importlib.import_module(name=module_name)
        except (ImportError, AttributeError, ValueError) as error:
            raise PluginNotFoundError(error) from error
        return getattr(module_obj, name.split(".")[-1])

    @staticmethod
    def load_installed_plugins() -> Plugins:
        """Search and load every installed plugin through entry points.

        Returns:
            Providers and checkers.
        """
        providers = {}
        checkers = {}
        entrypoints = entry_points()

        # TODO: Remove first block once support for Python < 3.12 is dropped.
        if sys.version_info < (3, 12):
            eps = next(eps for group, eps in entrypoints.items() if group.startswith("archan"))
        else:
            eps = entrypoints.select(group="archan")

        for entry_point in eps:
            obj = entry_point.load()
            if issubclass(obj, Provider):
                providers[entry_point.name] = obj
            elif issubclass(obj, Checker):
                checkers[entry_point.name] = obj
        return Plugins(providers=providers, checkers=checkers)

    @staticmethod
    def lint(config: dict) -> None:
        """Verify the contents of the configuration dictionary.

        Parameters:
            config: A configuration dictionary.

        Raises:
            ConfigError: If the config object is not a dictionary, or doesn't have an 'analysis' item.
        """
        if not isinstance(config, dict):
            raise ConfigError("config must be a dict")
        if "analysis" not in config:
            raise ConfigError('config must have "analysis" item')

    @staticmethod
    def from_file(path: str) -> Config:
        """Return a ``Config`` instance by reading a configuration file.

        Parameters:
            path: The config file path.

        Returns:
            The config object.
        """
        with open(path) as stream:
            obj = yaml.safe_load(stream)
        Config.lint(obj)
        return Config(config_dict=obj)

    @staticmethod
    def find() -> str | None:
        """Find the configuration file if any.

        Returns:
            The path to a configuration file.
        """
        names = ("archan.yml", "archan.yaml", ".archan.yml", ".archan.yaml")
        current_dir = os.getcwd()
        configconfig_file = os.path.join(current_dir, ".configconfig")
        default_config_dir = os.path.join(current_dir, "config")
        if os.path.isfile(configconfig_file):
            logger.debug(f"Reading {configconfig_file} to get config folder path")
            with open(configconfig_file) as stream:
                config_dir = os.path.join(current_dir, stream.read()).strip()
        elif os.path.isdir(default_config_dir):
            config_dir = default_config_dir
        else:
            config_dir = current_dir
        logger.debug(f"Config folder = {config_dir}")
        for name in names:
            config_file = os.path.join(config_dir, name)
            logger.debug(f"Searching for config file at {config_file}")
            if os.path.isfile(config_file):
                logger.debug(f"Found {config_file}")
                return config_file
        logger.debug("No config file found")
        return None

    @staticmethod
    def default_config(file_path: str | None = None) -> Config:
        """Return a default configuration instance.

        Parameters:
            file_path: Optional file path to configuration file.

        Returns:
            The config object.
        """
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
                    },
                },
            },
        )

    @staticmethod
    def inflate_plugin_list(plugin_list: list, inflate_plugin: Callable) -> list[Checker | Provider]:
        """Inflate a list of strings/dictionaries to a list of plugin instances.

        Parameters:
            plugin_list: a list of str/dict.
            inflate_plugin: the method to inflate the plugin.

        Returns:
            A plugin instances list.

        Raises:
            ValueError: When a dictionary item contains more than one key.
        """
        plugins = []
        for plugin_def in plugin_list:
            if isinstance(plugin_def, str):
                try:
                    plugins.append(inflate_plugin(plugin_def))
                except PluginNotFoundError as error:
                    logger.error(f"Could not import plugin identified by {plugin_def}. Exception: {error}.")
            elif isinstance(plugin_def, dict):
                if len(plugin_def) > 1:
                    raise ValueError("When using a plugin list, each dictionary item must contain only one key.")
                identifier = next(iter(plugin_def.keys()))
                definition = plugin_def[identifier]
                try:
                    plugins.append(inflate_plugin(identifier, definition))
                except PluginNotFoundError as error:
                    logger.error(
                        f"Could not import plugin identified by {identifier}. "
                        f"Inflate method: {inflate_plugin}. Exception: {error}.",
                    )
        return plugins

    @staticmethod
    def inflate_plugin_dict(plugin_dict: dict, inflate_plugin: Callable) -> list[Checker | Provider]:
        """Inflate a list of strings/dictionaries to a list of plugin instances.

        Parameters:
            plugin_dict: A dict of dict.
            inflate_plugin: The method to inflate the plugin.

        Returns:
            A plugin instances list.
        """
        plugins = []
        for identifier, definition in plugin_dict.items():
            try:
                plugins.append(inflate_plugin(identifier, definition))
            except PluginNotFoundError as error:
                logger.error(f"Could not import plugin identified by {identifier}. Exception: {error}")
        return plugins

    @staticmethod
    def inflate_nd_checker(identifier: str, definition: bool | dict) -> Checker:
        """Inflate a no-data checker from a basic definition.

        Parameters:
            identifier: The no-data checker identifier / name.
            definition: A boolean acting as "passes" or a full
                dict definition with "passes" and "allow_failure".

        Returns:
            A checker instance.

        Raises:
            ValueError: When the definition type is not bool or dict.
        """
        if isinstance(definition, bool):
            return Checker(name=identifier, passes=definition)
        if isinstance(definition, dict):
            return Checker(definition.pop("name", identifier), **definition)
        raise ValueError(f"{type(definition)} type is not supported for no-data checkers, use bool or dict")

    @staticmethod
    def cleanup_definition(definition: dict) -> None:
        """Clean-up a definition (remove name, description and arguments).

        Parameters:
            definition: The definition to clean.
        """
        definition.pop("name", "")
        definition.pop("description", "")
        definition.pop("arguments", "")

    @property
    def available_providers(self) -> dict[str, type[Provider]]:
        """Return the available providers.

        Returns:
            The available providers.
        """
        return self.plugins.providers

    @property
    def available_checkers(self) -> dict[str, type[Checker]]:
        """Return the available checkers.

        Returns:
            The available checkers.
        """
        return self.plugins.checkers

    def get_plugin(self, identifier: str, cls: type | None = None) -> type[Checker | Provider]:
        """Return the plugin corresponding to the given identifier and type.

        Parameters:
            identifier: Identifier of the plugin.
            cls: One of checker / provider.

        Returns:
            Checker/Provider: plugin class.
        """
        if (cls is None or cls == "provider") and identifier in self.available_providers:
            return self.available_providers[identifier]
        if (cls is None or cls == "checker") and identifier in self.available_checkers:
            return self.available_checkers[identifier]
        return Config.load_local_plugin(identifier)

    def get_provider(self, identifier: str) -> type[Provider]:
        """Return the provider class corresponding to the given identifier.

        Parameters:
            identifier: The provider identifier.

        Returns:
            The provider.
        """
        return self.get_plugin(identifier, cls="provider")  # type: ignore[arg-type,return-value]

    def get_checker(self, identifier: str) -> type[Checker]:
        """Return the checker class corresponding to the given identifier.

        Parameters:
            identifier: The checker identifier.

        Returns:
            The checker.
        """
        return self.get_plugin(identifier, cls="checker")  # type: ignore[arg-type,return-value]

    def provider_from_dict(self, dct: dict) -> Provider | None:
        """Return a provider instance from a dict object.

        Parameters:
            dct: The dictionary describing the provider.

        Returns:
            The provider.
        """
        provider_identifier = next(iter(dct.keys()))
        provider_class = self.get_provider(provider_identifier)
        if provider_class:
            return provider_class(**dct[provider_identifier])
        return None

    def checker_from_dict(self, dct: dict) -> Checker | None:
        """Return a checker instance from a dict object.

        Parameters:
            dct: The dictionary describing the checker.

        Returns:
            The checker.
        """
        checker_identifier = next(iter(dct.keys()))
        checker_class = self.get_checker(checker_identifier)
        if checker_class:
            return checker_class(**dct[checker_identifier])
        return None

    def inflate_plugin(
        self,
        identifier: str,
        definition: dict | None = None,
        cls: str | None = None,
    ) -> Checker | Provider:
        """Inflate a plugin thanks to it's identifier, definition and class.

        Parameters:
            identifier: The plugin identifier.
            definition: The kwargs to instantiate the plugin with.
            cls: "provider", "checker", or None.

        Returns:
            Instance of plugin.
        """
        real_cls = self.get_plugin(identifier, cls)  # type: ignore[arg-type]
        # TODO: implement re-usability of plugins?
        # same instances shared across analyses (to avoid re-computing stuff)
        return real_cls(**definition or {})

    def inflate_plugins(
        self,
        plugins_definition: list | dict,
        inflate_method: Callable,
    ) -> list[Checker | Provider]:
        """Inflate multiple plugins based on a list/dict definition.

        Parameters:
            plugins_definition: The plugins definitions.
            inflate_method: The method to indlate each plugin.

        Returns:
            A list of plugin instances.

        Raises:
            ValueError: When the definition type is not list or dict.
        """
        if isinstance(plugins_definition, (list, tuple)):
            return self.inflate_plugin_list(plugins_definition, inflate_method)
        if isinstance(plugins_definition, dict):
            return self.inflate_plugin_dict(plugins_definition, inflate_method)
        raise ValueError(f"{type(plugins_definition)} type is not supported for a plugin list, use list or dict")

    def inflate_provider(self, identifier: str, definition: dict | None = None) -> Provider:
        """Shortcut to inflate a provider.

        Parameters:
            identifier: The provider identifier.
            definition: The provider definition.

        Returns:
            A provider.
        """
        return self.inflate_plugin(identifier, definition, "provider")  # type: ignore[return-value]

    def inflate_checker(self, identifier: str, definition: dict | None = None) -> Checker:
        """Shortcut to inflate a checker.

        Parameters:
            identifier: The checker identifier.
            definition: The checker definition.

        Returns:
            A checker.
        """
        return self.inflate_plugin(identifier, definition, "checker")  # type: ignore[return-value]

    def inflate_providers(self, providers_definition: list | dict) -> list[Provider]:
        """Shortcut to inflate multiple providers.

        Parameters:
            providers_definition: The providers definitions.

        Returns:
            Multiple providers.
        """
        return self.inflate_plugins(providers_definition, self.inflate_provider)  # type: ignore[return-value]

    def inflate_checkers(self, checkers_definition: list | dict) -> list[Checker]:
        """Shortcut to inflate multiple checkers.

        Parameters:
            checkers_definition: The checkers definitions.

        Returns:
            Multiple checkers.
        """
        return self.inflate_plugins(checkers_definition, self.inflate_checker)  # type: ignore[return-value]

    def inflate_analysis_group(self, identifier: str, definition: dict) -> AnalysisGroup:
        """Inflate a whole analysis group.

        An analysis group is a section defined in the YAML file.

        Parameters:
            identifier: The group identifier.
            definition: The group definition.

        Returns:
            An instance of AnalysisGroup.

        Raises:
            ValueError: When identifier targets a plugin of a certain type,
                and the definition does not contain the entry for the
                other-type plugins (providers <-> checkers).
        """
        providers_definition = definition.pop("providers", None)
        checkers_definition = definition.pop("checkers", None)

        analysis_group = AnalysisGroup()

        try:
            first_plugin = self.inflate_plugin(identifier, definition)
        except PluginNotFoundError as error:
            logger.warning(
                f"Could not find any plugin identified by {identifier}, considering entry as group name. Exception: {error}.",
            )

            analysis_group.name = definition.pop("name", identifier)
            analysis_group.description = definition.pop("description", None)

            if bool(providers_definition) != bool(checkers_definition):
                raise ValueError(
                    "when declaring an analysis group with a name, you must "
                    'either declare both "providers" and "checkers" or none.',
                ) from error

            if providers_definition and checkers_definition:
                analysis_group.providers.extend(self.inflate_providers(providers_definition))
                analysis_group.checkers.extend(self.inflate_checkers(checkers_definition))
        else:
            if isinstance(first_plugin, Checker):
                analysis_group.checkers.append(first_plugin)

                if providers_definition is None:
                    raise ValueError(
                        "when declaring an analysis group with a checker "
                        "identifier, you must also declare providers with "
                        'the "providers" key.',
                    )

                analysis_group.providers.extend(self.inflate_providers(providers_definition))

            elif isinstance(first_plugin, Provider):
                analysis_group.providers.append(first_plugin)

                if checkers_definition is None:
                    raise ValueError(
                        "when declaring an analysis group with a provider "
                        "identifier, you must also declare checkers with "
                        'the "checkers" key.',
                    )

                analysis_group.checkers.extend(self.inflate_checkers(checkers_definition))

        self.cleanup_definition(definition)

        for nd_identifier, nd_definition in definition.items():
            analysis_group.checkers.append(self.inflate_nd_checker(nd_identifier, nd_definition))

        return analysis_group

    def print_plugins(self) -> None:
        """Print the available plugins."""
        width = console_width()
        line = Style.BRIGHT + "=" * width + "\n"
        middle = int(width / 2)
        if self.available_providers:
            print(line + " " * middle + "PROVIDERS")  # noqa: T201
            for provider in sorted(self.available_providers.values(), key=lambda prv: prv.identifier):
                provider().print()
                print()  # noqa: T201
        if self.available_checkers:
            print(line + " " * middle + "CHECKERS")  # noqa: T201
            for checker in sorted(self.available_checkers.values(), key=lambda prv: prv.identifier):
                checker().print()
                print()  # noqa: T201
