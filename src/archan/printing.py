"""Printing module."""

from __future__ import annotations

import shutil
import textwrap

from colorama import Fore, Style

from archan.enums import ResultCode
from archan.logging import Logger

logger = Logger.get_logger(__name__)


def console_width(default: int = 80) -> int:
    """Return current console width.

    Parameters:
        default: Default value if width cannot be retrieved.

    Returns:
        Console width.
    """
    # only solution that works with stdin redirected from file
    # https://stackoverflow.com/questions/566746
    return shutil.get_terminal_size((default, 20)).columns


def pretty_description(description: str, wrap_at: int | None = None, indent: int = 0) -> str:
    """Return a pretty formatted string given some text.

    Parameters:
        description: String to format.
        wrap_at: Maximum length of a line.
        indent: Level of indentation.

    Returns:
        Pretty formatted string.
    """
    if wrap_at is None or wrap_at < 0:
        width = console_width(default=79)
        if wrap_at is None:
            wrap_at = width
        else:
            wrap_at += width

    indent_str = " " * indent
    text_wrapper = textwrap.TextWrapper(
        width=wrap_at,
        replace_whitespace=False,
        initial_indent=indent_str,
        subsequent_indent=indent_str,
    )
    new_desc = description.strip().split("\n")
    separators = [index for index, line in enumerate(new_desc) if not line]
    paragraphs = []
    if separators:
        start, end = 0, separators[0]
        paragraphs.append(new_desc[start:end])
        for sep_index in range(len(separators) - 1):
            start = end + 1
            end = separators[sep_index + 1]
            paragraphs.append(new_desc[start:end])
        paragraphs.append(new_desc[end + 1 :])
        return "\n\n".join(text_wrapper.fill(" ".join(prg)) for prg in paragraphs)
    return text_wrapper.fill(" ".join(new_desc))


class PrintableNameMixin:
    """Mixin to a print_name method to instances."""

    def print_name(self, indent: int = 0, end: str = "\n") -> None:
        """Print name with optional indent and end.

        Parameters:
            indent: Indentation.
            end: End of line.
        """
        print(Style.BRIGHT + " " * indent + self.name, end=end)  # type: ignore[attr-defined]


class PrintableArgumentMixin:
    """Mixin to add a print method to Argument instances."""

    def print(self, indent: int = 0) -> None:  # noqa: A003
        """Print self with optional indent.

        Parameters:
            indent: Indentation.
        """
        text = "{indent}{magenta}{name}{none} ({dim}{cls}{none}, default {dim}{default}{none})".format(
            indent=" " * indent,
            dim=Style.DIM,
            magenta=Fore.MAGENTA,
            none=Style.RESET_ALL,
            name=self.name,  # type: ignore[attr-defined]
            cls=self.cls,  # type: ignore[attr-defined]
            default=self.default,  # type: ignore[attr-defined]
        )

        if self.description:  # type: ignore[attr-defined]
            text += ":\n" + pretty_description(self.description, indent=indent + 2)  # type: ignore[attr-defined]

        print(text)


class PrintablePluginMixin:
    """Mixin to add a print method to plugin instances."""

    identifier: str
    name: str
    description: str

    def print(self) -> None:  # noqa: A003
        """Print self."""
        print(
            f"{Style.DIM}Identifier:{Style.RESET_ALL} {Fore.CYAN}{self.identifier}{Style.RESET_ALL}\n"
            f"{Style.DIM}Name:{Style.RESET_ALL} {self.name}\n"
            f"{Style.DIM}Description:{Style.RESET_ALL}\n{pretty_description(self.description, indent=2)}",
        )

        if hasattr(self, "argument_list") and self.argument_list:
            print(f"{Style.DIM}Arguments:{Style.RESET_ALL}")
            for argument in self.argument_list:
                argument.print(indent=2)


class PrintableResultMixin:
    """Mixin to add a print method to Result instances."""

    def print(self, indent: int = 2) -> None:  # noqa: A003
        """Print self with optional indent.

        Parameters:
            indent: Indentation.
        """
        status = {
            ResultCode.NOT_IMPLEMENTED: f"{Fore.YELLOW}not implemented{Style.RESET_ALL}",
            ResultCode.IGNORED: f"{Fore.YELLOW}failed (ignored){Style.RESET_ALL}",
            ResultCode.FAILED: f"{Fore.RED}failed{Style.RESET_ALL}",
            ResultCode.PASSED: f"{Fore.GREEN}passed{Style.RESET_ALL}",
        }.get(
            self.code,  # type: ignore[attr-defined]
        )
        print(
            "{bold}{group}{provider}{checker}: {none}{status}{none}".format(
                bold=Style.BRIGHT,
                group=(self.group.name + " – ") if self.group.name else "",  # type: ignore[attr-defined]
                provider=(self.provider.name + " – ") if self.provider else "",  # type: ignore[attr-defined]
                checker=self.checker.name,  # type: ignore[attr-defined]
                none=Style.RESET_ALL,
                status=status,
            ),
        )
        if self.messages:  # type: ignore[attr-defined]
            for message in self.messages.split("\n"):  # type: ignore[attr-defined]
                print(pretty_description(message, indent=indent))
            if self.checker.hint:  # type: ignore[attr-defined]
                print(pretty_description("Hint: " + self.checker.hint, indent=indent))  # type: ignore[attr-defined]
