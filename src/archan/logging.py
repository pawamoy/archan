"""Logging module."""

from __future__ import annotations

import logging
from typing import ClassVar

from colorama import Back, Fore, Style


class Logger:
    """Static class to store loggers."""

    loggers: ClassVar[dict[str, logging.Logger]] = {}
    level = None

    @staticmethod
    def set_level(level: int) -> None:
        """Set level of logging for all loggers.

        Parameters:
            level: Level of logging.
        """
        Logger.level = level
        for logger in Logger.loggers.values():
            logger.setLevel(level)

    @staticmethod
    def get_logger(name: str, level: int | None = None, fmt: str = ":%(lineno)d: %(message)s") -> logging.Logger:
        """Return a logger.

        Parameters:
            name: Name to pass to the logging module.
            level: Level of logging.
            fmt: Format string.

        Returns:
            Logger from ``logging.getLogger``.
        """
        if name not in Logger.loggers:
            if Logger.level is None and level is None:
                Logger.level = logging.ERROR
                level = logging.ERROR
            elif Logger.level is None:
                Logger.level = level
            elif level is None:
                level = Logger.level
            logger = logging.getLogger(name)
            logger_handler = logging.StreamHandler()
            logger_handler.setFormatter(LoggingFormatter(fmt=name + fmt))
            logger.addHandler(logger_handler)
            logger.setLevel(level)  # type: ignore[arg-type]
            Logger.loggers[name] = logger
        return Logger.loggers[name]


class LoggingFormatter(logging.Formatter):
    """Custom logging formatter."""

    def format(self, record: logging.LogRecord) -> str:  # noqa: A003
        """Override default format method.

        Parameters:
            record: A log record.

        Returns:
            The formatted record.
        """
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
        return f"{Style.RESET_ALL}{string}{Style.RESET_ALL} {super().format(record)}"
