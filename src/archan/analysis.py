"""Analysis module."""

from __future__ import annotations

import sys
from typing import TYPE_CHECKING

from tap.tracker import Tracker

from archan.enums import ResultCode
from archan.logging import Logger
from archan.printing import PrintableNameMixin, PrintableResultMixin

if TYPE_CHECKING:
    from archan.checkers import Checker
    from archan.config import Config
    from archan.providers import Provider

logger = Logger.get_logger(__name__)


class Analysis:
    """Analysis class.

    An instance of Analysis contains a Config object.
    Providers are first run to generate the data, then
    these data are all checked against every checker.
    """

    def __init__(self, config: Config):
        """Initialization method.

        Parameters:
            config: The configuration object to use for analysis.
        """
        self.config = config
        self.results: list[Result] = []

    @staticmethod
    def _get_checker_result(
        group: AnalysisGroup,
        checker: Checker,
        provider: Provider | None = None,
        nd: str = "",
    ) -> Result:
        logger.info(f"Run {nd}checker {checker.identifier or checker.name}")
        checker.run(provider.data if provider else None)
        return Result(group, provider, checker, *checker.result)

    def run(self, verbose: bool = True) -> None:  # noqa: FBT001, FBT002
        """Run the analysis.

        Generate data from each provider, then check these data with every
        checker, and store the analysis results.

        Parameters:
            verbose: Whether to immediately print the results or not.
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
                for checker in analysis_group.checkers:
                    result = self._get_checker_result(analysis_group, checker, nd="no-data-")
                    self.results.append(result)
                    analysis_group.results.append(result)
                    if verbose:
                        result.print()

    def print_results(self) -> None:
        """Print analysis results as text on standard output."""
        for result in self.results:
            result.print()

    def output_tap(self) -> None:
        """Output analysis results in TAP format."""
        tracker = Tracker(streaming=True, stream=sys.stdout)
        for group in self.config.analysis_groups:
            n_providers = len(group.providers)
            n_checkers = len(group.checkers)
            if not group.providers and group.checkers:
                test_suite = group.name
                description_lambda = lambda result: result.checker.name  # noqa: E731
            elif not group.checkers:
                logger.warning("Invalid analysis group (no checkers), skipping")
                continue
            elif n_providers > n_checkers:
                test_suite = group.checkers[0].name
                description_lambda = lambda result: result.provider.name  # noqa: E731
            else:
                test_suite = group.providers[0].name
                description_lambda = lambda result: result.checker.name  # noqa: E731

            for result in group.results:
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

    def output_json(self) -> None:
        """Output analysis results in JSON format."""

    @property
    def successful(self) -> bool:
        """Property to tell if the run was successful: no failures.

        Returns:
            True if the run was successful.
        """
        return all(result.code != ResultCode.FAILED for result in self.results)


class AnalysisGroup(PrintableNameMixin):
    """Placeholder for groups of providers and checkers."""

    def __init__(
        self,
        name: str | None = None,
        description: str | None = None,
        providers: list | None = None,
        checkers: list | None = None,
    ):
        """Initialization method.

        Parameters:
            name: The group name.
            description: The group description.
            providers: The list of providers.
            checkers: The list of checkers.
        """
        self.name = name
        self.description = description
        self.providers = providers or []
        self.checkers = checkers or []
        self.results: list[Result] = []


class Result(PrintableResultMixin):
    """Placeholder for analysis results."""

    def __init__(self, group: AnalysisGroup, provider: Provider, checker: Checker, code: int, messages: str):
        """Initialization method.

        Parameters:
            group: Parent group.
            provider: Parent Provider.
            checker: Parent Checker.
            code: Constant from Checker class.
            messages: Messages string.
        """
        self.group = group
        self.provider = provider
        self.checker = checker
        self.code = code
        self.messages = messages
