import shutil
import textwrap

from colorama import Back, Fore, Style

from ..logging import Logger


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

    indent = ' ' * indent
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


class PluginArgumentPrintMixin:
    """Placeholder to store descriptive values of arguments."""

    def get_help(self):
        """Property to return the help text for an argument."""
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
            text += ':\n' + pretty_description(self.description, indent=4)

        return text

    @property
    def help(self):
        return self.get_help()


class PluginPrintMixin:
    def print_name(self, indent=0, end='\n'):
        print(Style.BRIGHT + ' ' * indent + self.name, end=end)

    def get_help(self):
        """Return a help text for the current subclass of Provider."""
        if hasattr(self, 'argument_list') and self.argument_list:
            complement = '{bold}Arguments:{none}\n{arguments}{none}\n'.format(
                arguments='\n'.join([a.help for a in self.argument_list]))
        else:
            complement = ''
        return (
            '{bold}Identifier:{none} {blue}{identifier}{none}\n'
            '{bold}Name:{none} {name}\n'
            '{bold}Description:{none}\n{description}\n' + complement
        ).format(
            bold=Style.BRIGHT,
            blue=Back.BLUE + Fore.WHITE,
            none=Style.RESET_ALL,
            identifier=self.identifier,
            name=self.name,
            description=pretty_description(self.description, indent=2)
        )

    @property
    def help(self):
        return self.get_help()
