# Why does this file exist, and why not put this in `__main__`?
#
# You might be tempted to import things from `__main__` later,
# but that will cause problems: the code will get executed twice:
#
# - When you run `python -m archan` python will execute
#   `__main__.py` as a script. That means there won't be any
#   `archan.__main__` in `sys.modules`.
# - When you import `__main__` it will get executed again (as a module) because
#   there's no `archan.__main__` in `sys.modules`.

"""Module that contains the command line application."""

import argparse
import logging
import os
import sys
from typing import List, Optional

import colorama

from . import __version__
from .analysis import Analysis
from .config import Config
from .logging import Logger

logger = Logger.get_logger(__name__)


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
        raise argparse.ArgumentTypeError("%s is not a valid file path" % value)
    elif os.path.isdir(value):
        raise argparse.ArgumentTypeError("%s is a directory, not a regular file" % value)
    return value


def valid_level(value):
    """Validation function for parser, logging level argument."""
    value = value.upper()
    if getattr(logging, value, None) is None:
        raise argparse.ArgumentTypeError("%s is not a valid level" % value)
    return value


def get_parser() -> argparse.ArgumentParser:
    """
    Return the CLI argument parser.

    Returns:
        An argparse parser.
    """
    parser = argparse.ArgumentParser(
        prog="archan", add_help=False, description="Analysis of your architecture strength based on DSM data"
    )
    parser.add_argument(
        "-c",
        "--config",
        action="store",
        type=valid_file,
        dest="config_file",
        metavar="FILE",
        help="Configuration file to use.",
    )
    parser.add_argument(
        "-h", "--help", action="help", default=argparse.SUPPRESS, help="Show this help message and exit."
    )
    parser.add_argument(
        "-i",
        "--input",
        action="store",
        type=valid_file,
        dest="input_file",
        metavar="FILE",
        help="Input file containing CSV data.",
    )
    parser.add_argument(
        "-l",
        "--list-plugins",
        action="store_true",
        dest="list_plugins",
        default=False,
        help="Show the available plugins. Default: false.",
    )
    parser.add_argument(
        "--no-color", action="store_true", dest="no_color", default=False, help="Do not use colors. Default: false."
    )
    parser.add_argument(
        "--no-config",
        action="store_true",
        dest="no_config",
        default=False,
        help="Do not load configuration from file. Default: false.",
    )
    parser.add_argument(
        "-v",
        "--verbose-level",
        action="store",
        dest="level",
        type=valid_level,
        default="ERROR",
        help="Level of verbosity.",
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version="archan %s" % __version__,
        help="Show the current version of the program and exit.",
    )
    return parser


def main(args: Optional[List[str]] = None) -> int:
    """
    Run the main program.

    This function is executed when you type `archan` or `python -m archan`.

    Arguments:
        args: Arguments passed from the command line.

    Returns:
        An exit code.
    """
    parser = get_parser()
    opts = parser.parse_args(args=args)
    Logger.set_level(opts.level)

    colorama_args = {"autoreset": True}
    if opts.no_color:
        colorama_args["strip"] = True
    colorama.init(**colorama_args)

    config = None
    if opts.no_config:
        logger.info("--no-config flag used, use default configuration")
        if opts.input_file:
            logger.info("Input file specified: %s" % opts.input_file)
            file_path = opts.input_file
        else:
            logger.info("No input file specified, will read standard input")
            file_path = sys.stdin
        config = Config.default_config(file_path)
    else:
        if opts.config_file:
            logger.info("Configuration file specified: %s" % opts.config_file)
            config_file = opts.config_file
        else:
            logger.info("No configuration file specified, searching")
            config_file = Config.find()
        if config_file:
            logger.info("Load configuration from %s" % config_file)
            config = Config.from_file(config_file)
        if config is None:
            logger.info("No configuration file found, use default one")
            config = Config.default_config()

    logger.debug("Configuration = {}".format(config))
    logger.debug("Plugins loaded = {}".format(config.plugins))

    if opts.list_plugins:
        logger.info("Print list of plugins")
        config.print_plugins()
        return 0

    logger.info("Run analysis")
    analysis = Analysis(config)
    try:
        analysis.run(verbose=False)
        logger.info("Analysis successful: %s" % analysis.successful)
        logger.info("Output results as TAP")
        analysis.output_tap()
        return 0 if analysis.successful else 1
    except KeyboardInterrupt:
        logger.info("Keyboard interruption, aborting")
        return 130
