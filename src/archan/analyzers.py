# -*- coding: utf-8 -*-

"""Analyzer module."""

from colorama import Back, Fore, Style

from .checkers import (
    Checker, CompleteMediation, EconomyOfMechanism, LayeredArchitecture,
    LeastCommonMechanism, OpenDesign)
from .providers import CSVInput
from .utils import Logger, pretty_description


class Analyzer(object):
    identifier = 'archan.GenericAnalyzer'
    name = 'Generic analyzer'
    description = ''
    providers = []
    checkers = []

    @classmethod
    def get_help(cls):
        return (
            '{bold}Name:{none} {blue}{name}{none}\n'
            '{bold}Description:{none}\n{description}\n'
            '{bold}Providers:{none} {providers}\n'
            '{bold}Checkers:{none} {checkers}\n'
        ).format(
            bold=Style.BRIGHT,
            blue=Back.BLUE + Fore.WHITE,
            none=Style.RESET_ALL,
            name=cls.name,
            description=pretty_description(cls.description, indent='  '),
            providers=','.join([p.name for p in cls.providers]),
            checkers=','.join([c.name for c in cls.checkers])
        )

    def __init__(self, identifier=None, name=None, description=None,
                 providers=None, checkers=None):
        self.logger = Logger.get_logger(__name__)

        if identifier is not None:
            self.identifier = identifier
        if name is not None:
            self.name = name
        if description is not None:
            self.description = description
        if providers is not None:
            self.providers = providers
        if checkers is not None:
            self.checkers = checkers
        self.results = []

        if not self.providers:
            self.logger.error('No providers in analyzer %s' % self.name)
        if not self.checkers:
            self.logger.error('No checkers in analyzer %s' % self.name)

    @property
    def help(self):
        return self.__class__.get_help()

    def run(self, verbose=True):
        self.results.clear()
        for provider in self.providers:
            provider.run()
        for provider in self.providers:
            for checker in self.checkers:
                result = AnalysisResult(
                    self, provider, checker, checker.run(provider.dsm))
                self.results.append(result)
                if verbose:
                    result.print()

    def collect_results(self):
        if not self.results:
            self.run(verbose=False)
        return self.results


class DefaultAnalyzer(Analyzer):
    identifier = 'archan.DefaultAnalyzer'
    name = 'Default Archan analyzer'
    description = 'Analyze internal dependencies from CSV.'

    providers = [
        CSVInput()
    ]

    checkers = [
        CompleteMediation(),
        EconomyOfMechanism(),
        LayeredArchitecture(),
        LeastCommonMechanism(),
        OpenDesign(),
    ]


class AnalysisResult(object):
    def __init__(self, analyzer, provider, checker, result):
        self.analyzer = analyzer
        self.provider = provider
        self.checker = checker
        self.result = result

    @property
    def code(self):
        return self.result[0]

    @property
    def messages(self):
        return self.result[1]

    def print(self, analyzer=True, provider=True):
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
        if analyzer:
            print(Style.BRIGHT + 'Analyzer: ' + self.analyzer.name)
        if provider:
            print(Style.BRIGHT + 'Provider: ' + self.provider.name)
        print('%s: ' % (Style.BRIGHT + self.checker.name), end='')
        print(status)
        if self.messages:
            for message in self.messages.split('\n'):
                print(pretty_description(message, indent='  '))
            if self.checker.hint:
                print(pretty_description(
                    'Hint: ' + self.checker.hint, indent='  '))
