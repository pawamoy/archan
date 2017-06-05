# -*- coding: utf-8 -*-

"""Analyzer module."""


class Analyzer(object):
    def __init__(self, providers, checkers):
        self.providers = providers
        self.checkers = checkers
        self.results = []

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
