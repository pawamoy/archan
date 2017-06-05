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
import os
import sys

from . import __version__
from .providers import CSVFileProvider
from .config import Config


def valid_file(value):
    """
    Check if given file exists and is a regular file.

    Args:
        value (str): path to the file.

    Raises:
        argparse.ArgumentTypeError: if not valid.

    Returns:
        str: original value argument.
    """
    if not value:
        raise argparse.ArgumentTypeError("'' is not a valid file path")
    elif not os.path.exists(value):
        raise argparse.ArgumentTypeError("%s is not a valid file path" %
                                         value)
    elif os.path.isdir(value):
        raise argparse.ArgumentTypeError("%s is a directory, "
                                         "not a regular file" % value)
    return value


parser = argparse.ArgumentParser(
    add_help=False,
    description='analysis of your architecture strength based on DSM data')
parser.add_argument('-c', '--config', action='store', type=valid_file,
                    dest='config_file', help='Configuration file to use.')
parser.add_argument('-h', '--help', action='help', default=argparse.SUPPRESS,
                    help='Show this help message and exit.')
parser.add_argument('-v', '--version', action='version',
                    version='archan %s' % __version__,
                    help='Show the current version of the program and exit.')
parser.add_argument('-l', '--list-plugins', action='store_true',
                    dest='list_plugins', default=False,
                    help='Show the available plugins. Default: false.')
parser.add_argument('--no-config', action='store_true', dest='no_config',
                    default=False, help='Do not load configuration from file. '
                                        'Default: false.')
parser.add_argument('-i', '--input', action='store', type=valid_file,
                    dest='input_file', help='Input file containing CSV data.')


def main(args=None):
    """Main function."""

    args = parser.parse_args(args=args)

    config = None
    if not args.no_config:
        if args.config_file:
            config_file = args.config_file
        else:
            config_file = Config.find()
        if config_file:
            config = Config.from_file(config_file)
    if config is None:
        config = Config.default_config()

    if args.list_plugins:
        for analyzer in config.available_analyzers:
            print(analyzer.get_help())
        for provider in config.available_providers:
            print(provider.get_help())
        for checker in config.available_checkers:
            print(checker.get_help())
        return

    config.run()

    if args.no_config and not args.input_file:
        green = '\033[;32m'
        yellow = '\033[;33m'
        red = '\033[;31m'
        blue = '\033[;34m'
        default = '\033[;39m'

        dsm = CSVFileProvider().get_dsm(file_path=sys.stdin)

        # report = archan.check(dsm)
        # for criterion, (result, messages) in report.items():
        #     print('%s :%s' % ('{:<25}'.format(criterion.title), {
        #         Criterion.NOT_IMPLEMENTED: '{}not implemented{}'.format(yellow, default),
        #         Criterion.IGNORED: 'ignored',
        #         Criterion.FAILED: '{}failed{}'.format(red, default),
        #         Criterion.PASSED: '{}passed{}'.format(green, default),
        #     }.get(result)))
        #     if messages:
        #         print(messages)
        return
