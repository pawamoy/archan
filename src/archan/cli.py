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
import logging
import os
import sys

import colorama

from . import __version__
from .config import Config
from .utils import Logger


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
        raise argparse.ArgumentTypeError(
            "%s is not a valid file path" % value)
    elif os.path.isdir(value):
        raise argparse.ArgumentTypeError(
            "%s is a directory, not a regular file" % value)
    return value


def valid_level(value):
    """Validation function for parser, logging level argument."""
    value = value.upper()
    if getattr(logging, value, None) is None:
        raise argparse.ArgumentTypeError("%s is not a valid level" % value)
    return value


def get_parser():
    """Return a parser for the command-line arguments."""
    parser = argparse.ArgumentParser(
        add_help=False,
        description='Analysis of your architecture strength based on DSM data')
    parser.add_argument(
        '-c', '--config', action='store', type=valid_file, dest='config_file',
        metavar='FILE', help='Configuration file to use.')
    parser.add_argument(
        '-h', '--help', action='help', default=argparse.SUPPRESS,
        help='Show this help message and exit.')
    parser.add_argument(
        '-i', '--input', action='store', type=valid_file, dest='input_file',
        metavar='FILE', help='Input file containing CSV data.')
    parser.add_argument(
        '-l', '--list-plugins', action='store_true', dest='list_plugins',
        default=False, help='Show the available plugins. Default: false.')
    parser.add_argument(
        '--no-color', action='store_true', dest='no_color', default=False,
        help='Do not use colors. Default: false.')
    parser.add_argument(
        '--no-config', action='store_true', dest='no_config', default=False,
        help='Do not load configuration from file. Default: false.')
    parser.add_argument(
        '-v', '--verbose-level', action='store', dest='level',
        type=valid_level, default='ERROR', help='Level of verbosity.')
    parser.add_argument(
        '-V', '--version', action='version', version='archan %s' % __version__,
        help='Show the current version of the program and exit.')
    return parser


def main(args=None):
    """Main function."""
    parser = get_parser()
    args = parser.parse_args(args=args)
    Logger.set_level(args.level)
    logger = Logger.get_logger(__name__)

    colorama_args = {'autoreset': True}
    if args.no_color:
        colorama_args['strip'] = True
    colorama.init(**colorama_args)

    config = None
    if args.no_config:
        logger.info('No configuration flag used, use default configuration')
        if args.input_file:
            file_path = args.input_file
        else:
            file_path = sys.stdin
        config = Config.default_config(file_path)
    else:
        if args.config_file:
            logger.ingo('Configuration file specified: %s' % args.config_file)
            config_file = args.config_file
        else:
            logger.info('No configuration file specified, searching')
            config_file = Config.find()
        if config_file:
            logger.info('Load configuration from %s' % config_file)
            config = Config.from_file(config_file)
        if config is None:
            logger.info('Use default configuration')
            config = Config.default_config()

    if args.list_plugins:
        logger.info('Print list of plugins')
        logger.debug('Plugins = {}'.format(config.plugins))
        config.print_plugins()
        return

    logger.info('Run analysis with configuration = %s' % config)
    config.run()
    config.print_results()
    return 0 if config.successful else 1
