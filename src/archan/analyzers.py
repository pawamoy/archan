# -*- coding: utf-8 -*-

"""Analyzer module."""

from colorama import Fore, Style

from .checkers import (
    CompleteMediation, CodeClean, EconomyOfMechanism, LayeredArchitecture,
    LeastCommonMechanism, LeastPrivileges, OpenDesign, SeparationOfPrivileges)
from .providers import CSVInput
from .utils import pretty_description


class Analyzer(object):
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
            blue=Fore.BLUE + Style.BRIGHT,
            none=Style.RESET_ALL,
            name=cls.name,
            description=pretty_description(cls.description, indent='  '),
            providers=','.join([p.name for p in cls.providers]),
            checkers=','.join([c.name for c in cls.checkers])
        )

    def __init__(self, providers=None, checkers=None):
        if providers is not None:
            self.providers = providers
        if checkers is not None:
            self.checkers = checkers
        self.results = []

    @property
    def help(self):
        return self.__class__.get_help()

    def run(self):
        self.results.clear()
        for provider in self.providers:
            provider.run()
        for provider in self.providers:
            for checker in self.checkers:
                self.results.append({
                    'provider': provider,
                    'checker': checker,
                    'result': checker.run(provider.dsm)
                })

    def collect_results(self):
        if not self.results:
            self.run()
        return self.results


class DefaultAnalyzer(Analyzer):
    name = 'archan.DefaultAnalyzer'
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
