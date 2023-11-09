"""Provider module."""

from __future__ import annotations

import sys
from typing import Any

from archan import Argument, Provider
from archan.dsm import DesignStructureMatrix
from archan.logging import Logger

logger = Logger.get_logger(__name__)


class CSVInput(Provider):
    """Provider to read DSM from CSV data."""

    identifier = "archan.CSVInput"
    name = "CSV Input"
    description = "Parse a CSV file to provide a matrix."
    argument_list = (
        Argument("file_path", str, "Path to the CSV file to parse.", "sys.stdin"),
        Argument("delimiter", str, "Delimiter used in the CSV file.", ","),
        Argument("categories_delimiter", str, "If set, used as delimiter for categories."),
    )

    def get_data(
        self,
        file_path: str | None = None,
        delimiter: str = ",",
        categories_delimiter: str | None = None,
        **kwargs: Any,  # noqa: ARG002
    ) -> DesignStructureMatrix:
        """Implement get_dsm method from Provider class.

        Parse CSV to return an instance of DSM.

        Parameters:
            file_path: String path or None. If None, uses sys.stdin.
            delimiter: Character(s) used as delimiter for columns.
            categories_delimiter:
                Character(s) used as delimiter for categories and keys
                (first column).

        Returns:
            DSM: instance of DSM.
        """
        if file_path is None:
            logger.info("Read data from standard input")
            lines = [line.replace("\n", "") for line in sys.stdin]
        else:
            logger.info(f"Read data from file {file_path}")
            with open(file_path) as file:
                lines = list(file)
        columns = lines[0].rstrip("\n").split(delimiter)[1:]
        categories = None
        if categories_delimiter:
            columns, categories = zip(*[column.split(categories_delimiter, 1) for column in columns])  # type: ignore[assignment]
        size = len(columns)
        data = [list(map(int, line.split(delimiter)[1:])) for line in lines[1 : size + 1]]
        return DesignStructureMatrix(data, columns, categories)  # type: ignore[arg-type]


# FIXME: move this provider in its own repo? it's not ready
# class CodeIssuesAndSimilarities(Provider):
#     identifier = 'archan.CodeIssuesAndSimilarities'
#     name = 'Code Issues and Similarities'
#     description = 'Provide a matrix with number of issues in code in the ' \
#                   'diagonal cells, and similarites between modules ' \
#                   'in other cells.'
#
#     def issues_per_file(self, path):
#         try:
#             from prospector import ProspectorConfig, Prospector
#         except ImportError:
#             return None, ''
#
#         prospector = Prospector(ProspectorConfig())
#         prospector.execute()
#         number_of_issues = len(prospector.messages)
#         min_lines_of_code, max_lines_of_code = self.count_lines(path)
#         issue_percentage = (
#             (number_of_issues / min_lines_of_code * 100) +
#             (number_of_issues / max_lines_of_code * 100)) / 2
#         return issue_percentage
#
#     def count_lines(self, path):
#         # http://code.activestate.com/recipes/527746-line-of-code-counter/
#
#         def walk(root='.', recurse=True, pattern='*'):
#             """
#             Generator for walking a directory tree.
#
#             Starts at specified root folder, returning files
#             that match our pattern. Optionally will also
#             recurse through sub-folders.
#             """
#             for path, subdirs, files in os.walk(root):
#                 for name in files:
#                     if fnmatch.fnmatch(name, pattern):
#                         yield os.path.join(path, name)
#                 if not recurse:
#                     break
#
#         def loc(root='', recurse=True):
#             """
#             Count lines of code in two ways.
#
#             - maximal size (source LOC) with blank lines and comments
#             - minimal size (logical LOC) stripping same
#
#             Sum all Python files in the specified folder.
#             By default recurse through sub-folders.
#             """
#             count_mini, count_maxi = 0, 0
#             for fspec in walk(root, recurse, '*.py'):
#                 skip = False
#                 for line in open(fspec).readlines():
#                     count_maxi += 1
#
#                     line = line.strip()
#                     if line:
#                         if line.startswith('#'):
#                             continue
#                         if line.startswith('"""'):
#                             skip = not skip
#                             continue
#                         if not skip:
#                             count_mini += 1
#
#             return count_mini, count_maxi
#
#         return loc(path)
#
#     def get_sims(self, *packages):
#         from dependenpy import DSM as DependenpyDSM
#         from pylint.checkers.similar import Similar
#         dsm = DependenpyDSM(*packages, build_dependencies=False)
#         sim = Similar()
#         for submodule in dsm.submodules:
#             with open(submodule.path) as stream:
#                 sim.append_stream(submodule.absolute_name(), stream)
#         return sim._compute_sims()
#
#     def get_dsm(self, **kwargs):
#         pass
