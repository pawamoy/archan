# -*- coding: utf-8 -*-

"""Provider module."""

from colorama import Fore, Style

import os
import fnmatch
import sys

from .dsm import DSM
from .utils import Argument, pretty_description


class Provider(object):
    name = 'archan.AbstractProvider'
    description = ''
    arguments = ()

    @classmethod
    def get_help(cls):
        return (
            '{bold}Name:{none} {blue}{name}{none}\n'
            '{bold}Description:{none}\n{description}\n' +
            ('{bold}Arguments:{none}\n{arguments}\n' if cls.arguments else '')
        ).format(
            bold=Style.BRIGHT,
            blue=Fore.BLUE + Style.BRIGHT,
            none=Style.RESET_ALL,
            name=cls.name,
            description=pretty_description(cls.description, indent='  '),
            arguments='\n'.join([a.help for a in cls.arguments])
        )

    def __init__(self, **run_kwargs):
        self.run_kwargs = run_kwargs
        self.dsm = None

    @property
    def help(self):
        return self.__class__.get_help()

    def get_dsm(self, **kwargs):
        raise NotImplementedError

    def run(self):
        self.dsm = self.get_dsm(**self.run_kwargs)


class CSVInput(Provider):
    name = 'archan.CSVInput'
    description = 'Parse a CSV file to provide a matrix.'
    arguments = (
        Argument('file_path', str,
                 'Path to the CSV file to parse.', 'sys.stdin'),
        Argument('delimiter', str, 'Delimiter used in the CSV file.', ','),
        Argument('categories_delimiter', str,
                 'If set, used as delimiter for categories.')
    )

    def get_dsm(self, file_path=sys.stdin, delimiter=',',
                categories_delimiter=None):
        if file_path == sys.stdin:
            lines = [line.replace('\n', '') for line in file_path]
        else:
            with open(file_path) as f:
                lines = list(f)
        columns = lines[0].split(delimiter)[1:]
        categories = None
        if categories_delimiter:
            columns, categories = zip(*[c.split(categories_delimiter, 1)
                                        for c in columns])
        size = len(columns)
        data = [list(map(int, l.split(delimiter)[1:]))
                for l in lines[1:size + 1]]
        return DSM(data, columns, categories)


# FIXME: move this provider in its own repo? it's not ready
class CodeIssuesAndSimilarities(Provider):
    name = 'archan.CodeIssuesAndSimilarities'
    description = 'Parse a CSV file to provide a matrix.'

    def issues_per_file(self, path):
        try:
            from prospector import ProspectorConfig, Prospector
        except ImportError:
            return None, ''

        prospector = Prospector(ProspectorConfig())
        prospector.execute()
        number_of_issues = len(prospector.messages)
        min_lines_of_code, max_lines_of_code = self.count_lines(path)
        issue_percentage = (
            (number_of_issues / min_lines_of_code * 100) +
            (number_of_issues / max_lines_of_code * 100)) / 2
        return issue_percentage

    def count_lines(self, path):
        # http://code.activestate.com/recipes/527746-line-of-code-counter/

        def walk(root='.', recurse=True, pattern='*'):
            """
            Generator for walking a directory tree.

            Starts at specified root folder, returning files
            that match our pattern. Optionally will also
            recurse through sub-folders.
            """
            for path, subdirs, files in os.walk(root):
                for name in files:
                    if fnmatch.fnmatch(name, pattern):
                        yield os.path.join(path, name)
                if not recurse:
                    break

        def loc(root='', recurse=True):
            """
            Count lines of code in two ways.

            - maximal size (source LOC) with blank lines and comments
            - minimal size (logical LOC) stripping same

            Sum all Python files in the specified folder.
            By default recurse through sub-folders.
            """
            count_mini, count_maxi = 0, 0
            for fspec in walk(root, recurse, '*.py'):
                skip = False
                for line in open(fspec).readlines():
                    count_maxi += 1

                    line = line.strip()
                    if line:
                        if line.startswith('#'):
                            continue
                        if line.startswith('"""'):
                            skip = not skip
                            continue
                        if not skip:
                            count_mini += 1

            return count_mini, count_maxi

        return loc(path)

    def get_sims(self, *packages):
        from dependenpy import DSM
        from pylint.checkers.similar import Similar
        dsm = DSM(*packages, build_dependencies=False)
        sim = Similar()
        for m in dsm.submodules:
            with open(m.path) as stream:
                sim.append_stream(m.absolute_name(), stream)
        return sim._compute_sims()

    def get_dsm(self, *args, **kwargs):
        pass
