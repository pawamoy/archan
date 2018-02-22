# -*- coding: utf-8 -*-

"""Analysis module."""

from colorama import Fore, Style

from .plugins import Checker
from .plugins.printing import pretty_description
from .logging import Logger


logger = Logger.get_logger(__name__)


class Analysis:
    """
    Analysis class.

    An instance of Analysis contains a Config object.
    Providers are first run to generate the data, then
    these data are all checked against every checker.
    """

    def __init__(self, config):
        """
        Initialization method.

        Args:
            config (Config): the configuration object to use for analysis.
        """
        self.config = config
        self.results = []

    def run(self, verbose=True):
        """
        Run the analysis.

        Generate data from each provider, then check these data with every
        checker, and store the analysis results.

        Args:
            verbose (bool): whether to immediately print the results or not.
        """
        self.results.clear()

        for analysis_group in self.config.analysis_groups:
            if verbose:
                analysis_group.print_name()
            for provider in analysis_group.providers:
                logger.info('Run provider %s', provider.identifier)
                provider.run()
            for provider in analysis_group.providers:
                if verbose:
                    provider.print_name(indent=2)
                for checker in analysis_group.checkers:
                    if verbose:
                        checker.print_name(indent=4, end=': ')
                    logger.info('Run checker %s', checker.identifier)
                    result = Result(
                        analysis_group, provider, checker, *checker.run(provider.data))
                    self.results.append(result)
                    if verbose:
                        result.print(False, False, 6)
        return self.results

    def print_results(self):
        """Print the collected results."""
        # TODO

    @property
    def successful(self):
        """Property to tell if the run was successful: no failures."""
        for result in self.results:
            if result.code == Checker.FAILED:
                return False
        return True


class AnalysisGroup:
    def __init__(self, name=None, description=None, providers=None, checkers=None):
        self.name = name
        self.description = description
        self.providers = providers or []
        self.checkers = checkers or []

    def print_name(self, indent=0, end='\n'):
        print(Style.BRIGHT + ' ' * indent + self.name, end=end)


class Result(object):
    """Placeholder for analysis results."""

    def __init__(self, group, provider, checker, code, messages):
        """
        Initialization method.

        Args:
            group (AnalysisGroup): parent group.
            provider (Provider): parent Provider.
            checker (Checker): parent Checker.
            code (int): constant from Checker class.
            messages (str): messages string.
        """
        self.group = group
        self.provider = provider
        self.checker = checker
        self.code = code
        self.messages = messages

    def print(self, provider=True, checker=True, indent=2):
        """
        Print an analysis result.

        Args:
            provider (bool): whether to print the provider or not.
            checker (bool): whether to print the checker or not.
            indent (int): indent for messages and hints.
        """
        status = {
            Checker.NOT_IMPLEMENTED: '{}not implemented{}'.format(
                Fore.YELLOW, Style.RESET_ALL),
            Checker.IGNORED: '{}failed (ignored){}'.format(
                Fore.YELLOW, Style.RESET_ALL),
            Checker.FAILED: '{}failed{}'.format(
                Fore.RED, Style.RESET_ALL),
            Checker.PASSED: '{}passed{}'.format(
                Fore.GREEN, Style.RESET_ALL),
        }.get(self.code)
        if provider:
            print(Style.BRIGHT + self.provider.name, end=' – ')
        if checker:
            print('%s: ' % (Style.BRIGHT + self.checker.name), end='')
        print(Style.RESET_ALL + status)
        if self.messages:
            for message in self.messages.split('\n'):
                print(pretty_description(message, indent=indent))
            if self.checker.hint:
                print(pretty_description(
                    'Hint: ' + self.checker.hint, indent=indent))
