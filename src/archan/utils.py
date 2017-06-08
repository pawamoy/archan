# -*- coding: utf-8 -*-

"""Utils module."""

import logging
import subprocess
import textwrap

from colorama import Back, Fore, Style


def console_width(default=80):
    try:
        _, width = subprocess.check_output(['/bin/stty', 'size']).split()
        width = int(width)
    except subprocess.CalledProcessError:
        width = default
    return width


def pretty_description(description, wrap_at=None, indent=''):
    if wrap_at is None or wrap_at < 0:
        width = console_width(default=79)
        if wrap_at is None:
            wrap_at = width
        else:
            wrap_at += width

    text_wrapper = textwrap.TextWrapper(
        width=wrap_at, replace_whitespace=False,
        initial_indent=indent, subsequent_indent=indent)
    new_desc = []
    for line in description.split('\n'):
        new_desc.append(line.replace('\n', '').strip())
    while not new_desc[0]:
        del new_desc[0]
    while not new_desc[-1]:
        del new_desc[-1]
    separators = [i for i, l in enumerate(new_desc) if not l]
    paragraphs = []
    if separators:
        start, end = 0, separators[0]
        paragraphs.append(new_desc[start:end])
        for i in range(len(separators) - 1):
            start = end + 1
            end = separators[i + 1]
            paragraphs.append(new_desc[start:end])
        paragraphs.append(new_desc[end + 1:])
        return '\n\n'.join(text_wrapper.fill(' '.join(p)) for p in paragraphs)
    return text_wrapper.fill(' '.join(new_desc))


class Argument(object):
    def __init__(self, name, cls, description=None, default=None):
        self.name = name
        self.cls = cls
        self.description = description
        self.default = default

    def __str__(self):
        return '  %s (%s, default %s): %s' % (
            self.name, self.cls, self.default, self.description)

    @property
    def help(self):
        text = (
            '  {yellow}{name}{none} ({bold}{cls}{none}, '
            'default {bold}{default}{none})'
        ).format(
            bold=Style.BRIGHT,
            yellow=Back.YELLOW + Fore.BLACK,
            none=Style.RESET_ALL,
            name=self.name,
            cls=self.cls,
            default=self.default
        )

        if self.description:
            text += ':\n' + pretty_description(self.description, indent='    ')

        return text


class Logger(object):
    loggers = {}
    level = None

    @staticmethod
    def set_level(level):
        Logger.level = level
        for logger in Logger.loggers.values():
            logger.setLevel(level)

    @staticmethod
    def get_logger(name, level=None, fmt='%(message)s'):
        if name not in Logger.loggers:
            if Logger.level is None and level is None:
                Logger.level = level = logging.ERROR
            elif Logger.level is None:
                Logger.level = level
            elif level is None:
                level = Logger.level
            logger = logging.getLogger(name)
            logger_handler = logging.StreamHandler()
            format_string = '%s: ' % name + fmt
            logger_handler.setFormatter(LoggingFormatter(fmt=format_string))
            logger.addHandler(logger_handler)
            logger.setLevel(level)
            Logger.loggers[name] = logger
        return Logger.loggers[name]


class LoggingFormatter(logging.Formatter):
    def format(self, record):
        if record.levelno == logging.DEBUG:
            string = Back.WHITE + Fore.BLACK + ' debug '
        elif record.levelno == logging.INFO:
            string = Back.BLUE + Fore.WHITE + ' info '
        elif record.levelno == logging.WARNING:
            string = Back.YELLOW + Fore.BLACK + ' warning '
        elif record.levelno == logging.ERROR:
            string = Back.RED + Fore.WHITE + ' error '
        elif record.levelno == logging.CRITICAL:
            string = Back.BLACK + Fore.WHITE + ' critical '
        else:
            string = ''
        return string + Style.RESET_ALL + ' ' + super().format(record)
