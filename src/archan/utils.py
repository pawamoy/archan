# -*- coding: utf-8 -*-

"""Utils module."""

import textwrap
import subprocess

from colorama import Fore, Style


def console_width(default=80):
    try:
        _, width = subprocess.check_output(['stty', 'size']).split()
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
        paragraphs.append(new_desc[end+1:])
        return '\n\n'.join(text_wrapper.fill(' '.join(p)) for p in paragraphs)
    else:
        return text_wrapper.fill(' '.join(new_desc))


class Argument(object):
    def __init__(self, name, type, description=None, default=None):
        self.name = name
        self.type = type
        self.description = description
        self.default = default

    def __str__(self):
        return '  %s (%s, default %s): %s' % (
            self.name, self.type, self.default, self.description)

    @property
    def help(self):
        text = (
            '  {yellow}{name}{none} ({bold}{type}{none}, '
            'default {bold}{default}{none})'
        ).format(
            bold=Style.BRIGHT,
            yellow=Fore.YELLOW + Style.BRIGHT,
            none=Style.RESET_ALL,
            name=self.name,
            type=self.type,
            default=self.default
        )

        if self.description:
            text += ':\n' + pretty_description(self.description, indent='    ')

        return text
