"""Module that contains the command line application."""

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

from __future__ import annotations

import argparse
import logging
import os
import sys
from typing import Any

import colorama

from archan import debug
from archan.analysis import Analysis
from archan.config import Config
from archan.logging import Logger

logger = Logger.get_logger(__name__)


class _DebugInfo(argparse.Action):
    def __init__(self, nargs: int | str | None = 0, **kwargs: Any) -> None:
        super().__init__(nargs=nargs, **kwargs)

    def __call__(self, *args: Any, **kwargs: Any) -> None:  # noqa: ARG002
        debug.print_debug_info()
        sys.exit(0)


def valid_file(value: str) -> str:
    """Check if given file exists and is a regular file.

    Parameters:
        value: Path to the file.

    Raises:
        ArgumentTypeError: When value not valid.

    Returns:
        Original value argument.
    """
    if not value:
        raise argparse.ArgumentTypeError("'' is not a valid file path")
    if not os.path.exists(value):
        raise argparse.ArgumentTypeError(f"{value} is not a valid file path")
    if os.path.isdir(value):
        raise argparse.ArgumentTypeError(f"{value} is a directory, not a regular file")
    return value


def valid_level(value: str) -> str:
    """Validate the logging level argument for the parser.

    Parameters:
        value: The value provided on the command line.

    Raises:
        ArgumentTypeError: When value not valid.

    Returns:
        The validated level.
    """
    value = value.upper()
    if getattr(logging, value, None) is None:
        raise argparse.ArgumentTypeError(f"{value} is not a valid level")
    return value


def get_parser() -> argparse.ArgumentParser:
    """Return the CLI argument parser.

    Returns:
        An argparse parser.
    """
    parser = argparse.ArgumentParser(
        prog="archan",
        add_help=False,
        description="Analysis of your architecture strength based on DSM data",
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
        "-h",
        "--help",
        action="help",
        default=argparse.SUPPRESS,
        help="Show this help message and exit.",
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
        "--no-color",
        action="store_true",
        dest="no_color",
        default=False,
        help="Do not use colors. Default: false.",
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
        version=f"archan {debug.get_version()}",
        help="Show the current version of the program and exit.",
    )
    parser.add_argument("--debug-info", action=_DebugInfo, help="Print debug information.")
    return parser


def main(args: list[str] | None = None) -> int:
    """Run the main program.

    This function is executed when you type `archan` or `python -m archan`.

    Parameters:
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
            logger.info(f"Input file specified: {opts.input_file}")
            file_path = opts.input_file
        else:
            logger.info("No input file specified, will read standard input")
            file_path = None
        config = Config.default_config(file_path)
    else:
        if opts.config_file:
            logger.info(f"Configuration file specified: {opts.config_file}")
            config_file = opts.config_file
        else:
            logger.info("No configuration file specified, searching")
            config_file = Config.find()
        if config_file:
            logger.info(f"Load configuration from {config_file}")
            config = Config.from_file(config_file)
        if config is None:
            logger.info("No configuration file found, use default one")
            config = Config.default_config()

    logger.debug(f"Configuration = {config}")
    logger.debug(f"Plugins loaded = {config.plugins}")

    if opts.list_plugins:
        logger.info("Print list of plugins")
        config.print_plugins()
        return 0

    logger.info("Run analysis")
    analysis = Analysis(config)
    try:
        analysis.run(verbose=False)
    except KeyboardInterrupt:
        logger.info("Keyboard interruption, aborting")
        return 130
    logger.info(f"Analysis successful: {analysis.successful}")
    logger.info("Output results as TAP")
    analysis.output_tap()
    return 0 if analysis.successful else 1
