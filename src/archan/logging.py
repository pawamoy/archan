# -*- coding: utf-8 -*-

"""Logging module."""

from __future__ import absolute_import

import logging
from typing import Dict

from colorama import Back, Fore, Style


class Logger(object):
    """Static class to store loggers."""

    loggers: Dict[str, logging.Logger] = {}
    level = None

    @staticmethod
    def set_level(level):
        """
        Set level of logging for all loggers.

        Args:
            level (int): level of logging.
        """
        Logger.level = level
        for logger in Logger.loggers.values():
            logger.setLevel(level)

    @staticmethod
    def get_logger(name, level=None, fmt=":%(lineno)d: %(message)s"):
        """
        Return a logger.

        Args:
            name (str): name to pass to the logging module.
            level (int): level of logging.
            fmt (str): format string.

        Returns:
            logging.Logger: logger from ``logging.getLogger``.
        """
        if name not in Logger.loggers:
            if Logger.level is None and level is None:
                Logger.level = level = logging.ERROR
            elif Logger.level is None:
                Logger.level = level
            elif level is None:
                level = Logger.level
            logger = logging.getLogger(name)
            logger_handler = logging.StreamHandler()
            logger_handler.setFormatter(LoggingFormatter(fmt=name + fmt))
            logger.addHandler(logger_handler)
            logger.setLevel(level)
            Logger.loggers[name] = logger
        return Logger.loggers[name]


class LoggingFormatter(logging.Formatter):
    """Custom logging formatter."""

    def format(self, record):
        """Override default format method."""
        if record.levelno == logging.DEBUG:
            string = Back.WHITE + Fore.BLACK + " debug "
        elif record.levelno == logging.INFO:
            string = Back.BLUE + Fore.WHITE + " info "
        elif record.levelno == logging.WARNING:
            string = Back.YELLOW + Fore.BLACK + " warning "
        elif record.levelno == logging.ERROR:
            string = Back.RED + Fore.WHITE + " error "
        elif record.levelno == logging.CRITICAL:
            string = Back.BLACK + Fore.WHITE + " critical "
        else:
            string = ""
        return "{none}{string}{none} {super}".format(none=Style.RESET_ALL, string=string, super=super().format(record))
