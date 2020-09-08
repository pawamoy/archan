# -*- coding: utf-8 -*-

"""Printing module."""

import shutil
import textwrap

from colorama import Fore, Style

from .enums import ResultCode
from .logging import Logger

logger = Logger.get_logger(__name__)


def console_width(default=80):
    """
    Return current console width.

    Args:
        default (int): default value if width cannot be retrieved.

    Returns:
        int: console width.
    """
    # only solution that works with stdin redirected from file
    # https://stackoverflow.com/questions/566746
    return shutil.get_terminal_size((default, 20)).columns


def pretty_description(description, wrap_at=None, indent=0):
    """
    Return a pretty formatted string given some text.

    Args:
        description (str): string to format.
        wrap_at (int): maximum length of a line.
        indent (int): level of indentation.

    Returns:
        str: pretty formatted string.
    """
    if wrap_at is None or wrap_at < 0:
        width = console_width(default=79)
        if wrap_at is None:
            wrap_at = width
        else:
            wrap_at += width

    indent = " " * indent
    text_wrapper = textwrap.TextWrapper(
        width=wrap_at, replace_whitespace=False, initial_indent=indent, subsequent_indent=indent
    )
    new_desc = []
    for line in description.split("\n"):
        new_desc.append(line.replace("\n", "").strip())
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
        paragraphs.append(new_desc[end + 1 :])
        return "\n\n".join(text_wrapper.fill(" ".join(p)) for p in paragraphs)
    return text_wrapper.fill(" ".join(new_desc))


class PrintableNameMixin:
    """Mixin to a print_name method to instances."""

    def print_name(self, indent=0, end="\n"):
        """Print name with optional indent and end."""
        print(Style.BRIGHT + " " * indent + self.name, end=end)


class PrintableArgumentMixin:
    """Mixin to add a print method to Argument instances."""

    def print(self, indent=0):
        """Print self with optional indent."""
        text = ("{indent}{magenta}{name}{none} ({dim}{cls}{none}, " "default {dim}{default}{none})").format(
            indent=" " * indent,
            dim=Style.DIM,
            magenta=Fore.MAGENTA,
            none=Style.RESET_ALL,
            name=self.name,
            cls=self.cls,
            default=self.default,
        )

        if self.description:
            text += ":\n" + pretty_description(self.description, indent=indent + 2)

        print(text)


class PrintablePluginMixin:
    """Mixin to add a print method to plugin instances."""

    def print(self):
        """Print self."""
        print(
            "{dim}Identifier:{none} {cyan}{identifier}{none}\n"
            "{dim}Name:{none} {name}\n"
            "{dim}Description:{none}\n{description}".format(
                dim=Style.DIM,
                cyan=Fore.CYAN,
                none=Style.RESET_ALL,
                identifier=self.identifier,
                name=self.name,
                description=pretty_description(self.description, indent=2),
            )
        )

        if hasattr(self, "argument_list") and self.argument_list:
            print("{dim}Arguments:{none}".format(dim=Style.DIM, none=Style.RESET_ALL))
            for argument in self.argument_list:
                argument.print(indent=2)


class PrintableResultMixin:
    """Mixin to add a print method to Result instances."""

    def print(self, indent=2):
        """Print self with optional indent."""
        status = {
            ResultCode.NOT_IMPLEMENTED: "{}not implemented{}".format(Fore.YELLOW, Style.RESET_ALL),
            ResultCode.IGNORED: "{}failed (ignored){}".format(Fore.YELLOW, Style.RESET_ALL),
            ResultCode.FAILED: "{}failed{}".format(Fore.RED, Style.RESET_ALL),
            ResultCode.PASSED: "{}passed{}".format(Fore.GREEN, Style.RESET_ALL),
        }.get(self.code)
        print(
            "{bold}{group}{provider}{checker}: {none}{status}{none}".format(
                bold=Style.BRIGHT,
                group=(self.group.name + " – ") if self.group.name else "",
                provider=(self.provider.name + " – ") if self.provider else "",
                checker=self.checker.name,
                none=Style.RESET_ALL,
                status=status,
            )
        )
        if self.messages:
            for message in self.messages.split("\n"):
                print(pretty_description(message, indent=indent))
            if self.checker.hint:
                print(pretty_description("Hint: " + self.checker.hint, indent=indent))
