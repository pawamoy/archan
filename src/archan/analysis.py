"""Analysis module."""

import sys

from tap.tracker import Tracker

from archan.enums import ResultCode
from archan.logging import Logger
from archan.printing import PrintableNameMixin, PrintableResultMixin

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

        Arguments:
            config (Config): the configuration object to use for analysis.
        """
        self.config = config
        self.results = []

    @staticmethod
    def _get_checker_result(group, checker, provider=None, nd=""):
        logger.info(f"Run {nd}checker {checker.identifier or checker.name}")
        checker.run(provider.data if provider else None)
        return Result(group, provider, checker, *checker.result)

    def run(self, verbose: bool = True):
        """
        Run the analysis.

        Generate data from each provider, then check these data with every
        checker, and store the analysis results.

        Arguments:
            verbose: whether to immediately print the results or not.
        """
        self.results.clear()

        for analysis_group in self.config.analysis_groups:
            if analysis_group.providers:
                for provider in analysis_group.providers:
                    logger.info(f"Run provider {provider.identifier}")
                    provider.run()
                    for checker in analysis_group.checkers:
                        result = self._get_checker_result(analysis_group, checker, provider)
                        self.results.append(result)
                        analysis_group.results.append(result)
                        if verbose:
                            result.print()
            else:
                for checker in analysis_group.checkers:  # noqa: WPS440
                    result = self._get_checker_result(analysis_group, checker, nd="no-data-")
                    self.results.append(result)
                    analysis_group.results.append(result)
                    if verbose:
                        result.print()

    def print_results(self):
        """Print analysis results as text on standard output."""
        for result in self.results:
            result.print()

    def output_tap(self):
        """Output analysis results in TAP format."""
        tracker = Tracker(streaming=True, stream=sys.stdout)
        for group in self.config.analysis_groups:
            n_providers = len(group.providers)
            n_checkers = len(group.checkers)
            if not group.providers and group.checkers:
                test_suite = group.name
                description_lambda = lambda result: result.checker.name  # noqa: E731
            elif not group.checkers:  # noqa: WPS504
                logger.warning("Invalid analysis group (no checkers), skipping")
                continue
            elif n_providers > n_checkers:
                test_suite = group.checkers[0].name
                description_lambda = lambda result: result.provider.name  # noqa: E731
            else:
                test_suite = group.providers[0].name
                description_lambda = lambda result: result.checker.name  # noqa: E731

            for result in group.results:  # noqa: WPS440
                description = description_lambda(result)
                if result.code == ResultCode.PASSED:
                    tracker.add_ok(test_suite, description)
                elif result.code == ResultCode.IGNORED:
                    tracker.add_ok(test_suite, description + " (ALLOWED FAILURE)")
                elif result.code == ResultCode.NOT_IMPLEMENTED:
                    tracker.add_not_ok(test_suite, description, "TODO implement the test")
                elif result.code == ResultCode.FAILED:
                    message = "\n  message: ".join(result.messages.split("\n"))
                    tracker.add_not_ok(
                        test_suite,
                        description,
                        diagnostics=f"  ---\n  message: {message}\n  hint: {result.checker.hint}\n  ...",
                    )

    def output_json(self):
        """Output analysis results in JSON format."""

    @property
    def successful(self) -> bool:
        """
        Property to tell if the run was successful: no failures.

        Returns:
            True if the run was successful.
        """
        for result in self.results:
            if result.code == ResultCode.FAILED:
                return False
        return True


class AnalysisGroup(PrintableNameMixin):
    """Placeholder for groups of providers and checkers."""

    def __init__(self, name=None, description=None, providers=None, checkers=None):
        """
        Initialization method.

        Arguments:
            name (str): the group name.
            description (str): the group description.
            providers (list): the list of providers.
            checkers (list): the list of checkers.
        """
        self.name = name
        self.description = description
        self.providers = providers or []
        self.checkers = checkers or []
        self.results = []


class Result(PrintableResultMixin):
    """Placeholder for analysis results."""

    def __init__(self, group, provider, checker, code, messages):
        """
        Initialization method.

        Arguments:
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
