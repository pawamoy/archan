# -*- coding: utf-8 -*-

"""Provider module."""

import os
import fnmatch
import sys

from .utils import Argument


class Provider(object):
    name = 'Generic provider'
    description = ''
    arguments = ()

    def __init__(self, **run_kwargs):
        self.run_kwargs = run_kwargs
        self.dsm = None

    def get_dsm(self, **kwargs):
        raise NotImplementedError

    @classmethod
    def get_help(cls):
        return 'Name: %s\nDescription: %s\nArguments:\n%s\n' % (
            cls.name,
            cls.description,
            '\n'.join([str(a) for a in cls.arguments])
        )

    def run(self):
        self.dsm = self.get_dsm(**self.run_kwargs)


class CSVFileProvider(Provider):
    name = 'File provider'
    description = 'Parse a CSV file to provide a matrix.'
    arguments = (
        Argument('file_path', str, 'Path to the CSV file to parse.'),
        Argument('delimiter', str, 'Delimiter used in the CSV file.', ',')
    )

    def get_dsm(self, file_path='', delimiter=','):
        if not file_path:
            return {}
        if file_path == sys.stdin:
            lines = ''.join(file_path)
        else:
            with open(file_path) as f:
                lines = list(f)
        columns = lines[0].split(',')[1:]
        size = len(columns)
        data = [list(map(int, l.split(',')[1:])) for l in
                lines[1:size + 1]]
        return {'keys': columns, 'data': data}


# FIXME: move this provider in its own repo? it's not ready
class CodeCleanProvider(Provider):
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
