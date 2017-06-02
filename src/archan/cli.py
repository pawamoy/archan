# -*- coding: utf-8 -*-

"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later,
  but that will cause problems: the code will get executed twice:

  - When you run `python -marchan` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``archan.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``archan.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""

import argparse
import sys
from pprint import pprint

from .checker import Archan
from .criterion import Criterion
from .dsm import DesignStructureMatrix


parser = argparse.ArgumentParser(
    description='analysis of your architecture strength based on DSM data')


def main(args=None):
    """Main function."""

    green = '\033[;32m'
    yellow = '\033[;33m'
    red = '\033[;31m'
    blue = '\033[;34m'
    default = '\033[;39m'

    args = parser.parse_args(args=args)
    stdin_text = ''.join(sys.stdin)
    lines = stdin_text.split('\n')
    columns = lines[0].split(',')[1:]
    size = len(columns)
    data = [list(map(int, l.split(',')[1:])) for l in lines[1:size+1]]
    archan = Archan()
    dsm = DesignStructureMatrix(['app_module'] * size, columns, data)
    report = archan.check(dsm)
    for code, (result, messages) in report.items():
        print('%s :%s' % ('{:<25}'.format(code), {
            Criterion.NOT_IMPLEMENTED: '{}not implemented{}'.format(yellow, default),
            Criterion.IGNORED: 'ignored',
            Criterion.FAILED: '{}failed{}'.format(red, default),
            Criterion.PASSED: '{}passed{}'.format(green, default),
        }.get(result)))
        if messages:
            print(messages)
