# Archan

[![ci](https://github.com/pawamoy/archan/workflows/ci/badge.svg)](https://github.com/pawamoy/archan/actions?query=workflow%3Aci)
[![documentation](https://img.shields.io/badge/docs-mkdocs%20material-blue.svg?style=flat)](https://pawamoy.github.io/archan/)
[![pypi version](https://img.shields.io/pypi/v/archan.svg)](https://pypi.org/project/archan/)
[![gitpod](https://img.shields.io/badge/gitpod-workspace-blue.svg?style=flat)](https://gitpod.io/#https://github.com/pawamoy/archan)
[![gitter](https://badges.gitter.im/join%20chat.svg)](https://app.gitter.im/#/room/#archan:gitter.im)

Analysis of your architecture strength based on DSM data.

A Python module that analyzes your architecture strength
based on [Design Structure Matrix (DSM)][dsm] data.

Archan is a Python module that analyzes the strength of your
project architecture according to some criteria described in
["The Protection of Information in Computer Systems"][paper], written by
Jerome H. Saltzer and Michael D. Schroeder.

[dsm]: https://en.wikipedia.org/wiki/Design_structure_matrix
[paper]: https://www.cs.virginia.edu/~evans/cs551/saltzer/

## Features

- Usable directly on the command-line.
- Support for plugins. See for example the [Provider plugin][provider] in [dependenpy].
  You can also take a look at [django-meerkat], a Django app using Archan.
- Configurable through command-line or configuration file (YAML format).
- Read DSM data on standard input.

[dependenpy]: https://github.com/pawamoy/dependenpy
[django-meerkat]: https://github.com/pawamoy/django-meerkat
[provider]: https://github.com/pawamoy/dependenpy/blob/master/src/dependenpy/plugins.py

## Installation

With `pip`:

```bash
pip install archan
```

With [`pipx`](https://github.com/pipxproject/pipx):

```bash
python3.8 -m pip install --user pipx
pipx install archan
```

## Usage

Archan defines three main classes: Analyzer, Provider and Checker.
A provider is an object that will produce data and return it in the form of
a DSM (Design Structure Matrix). The checker is an object that
will analyze this DSM according to some criteria, and return a status code
saying if the criteria are verified or not. An analyzer is just a combination
of providers and checkers to run a analysis test suite.

### On the command-line

Examples:

```console
$ archan -h
usage: archan [-c FILE] [-h] [-i FILE] [-l] [--no-color] [--no-config] [-v]

Analysis of your architecture strength based on DSM data

optional arguments:
    -c FILE, --config FILE  Configuration file to use.
    -h, --help              Show this help message and exit.
    -i FILE, --input FILE   Input file containing CSV data.
    -l, --list-plugins      Show the available plugins. Default: false.
    --no-color              Do not use colors. Default: false.
    --no-config             Do not load configuration from file. Default: false.
    -v, --version           Show the current version of the program and exit.
```

```bash
# See a list of all supported Archan plugins
archan --list-plugins

# Archan can locate the configuration file automatically (See the Configuration section)
archan
# or a specific configuration can be specified
archan --config my_config.yml

# Archan can load DSM data in CSV format such as the output from dependenpy (install separately)
dependenpy pytest --format=csv --output pytest_dsm.csv

# Read CSV data from file (No configuration)
archan --no-config --input pytest_dsm.csv
# or read CSV data from STDIN
dependenpy pytest --format=csv | archan --no-config
```

## Configuration

Archan applies the following methods to find the configuration file folder:

1. read the contents of the file `.configconfig` in the current directory
   to get the path to the configuration directory,
2. use `config` folder in the current directory if it exists,
3. use the current directory.

It then searches for a configuration file named:

1. `archan.yml`
2. `archan.yaml`
3. `.archan.yml`
4. `.archan.yaml`

Format of the configuration file is as follow:

```yaml
analyzers: [list of strings and/or dict]
  - identifier: [optional string]
      name: [string]
      description: [string]
      providers: [string or list]
        - provider.Name: [as string or dict]
            provider_arguments: as key value pairs
      checkers: [string or list]
        - checker.Name: [as string or dict]
            checker_arguments: as key value pairs
```

It means you can write:

```yaml
analyzers:
  # a first analyzer with one provider and several checker
  - name: My first analyzer
      description: Optional description
      providers: just.UseThisProvider
      checkers:
        - and.ThisChecker
        - and.ThisOtherChecker:
            which: has
            some: arguments
  # a second analyzer with several providers and one checker
  - name: My second analyzer
      providers:
        - use.ThisProvider
      checkers: and.ThisChecker
  # a third analyzer, using its name directly
  - some.Analyzer
```

Every checker support an `ignore` argument, set to True or False (default).
If set to True, the check will not make the test suit fail.

You can reuse the same providers and checkers in different analyzers, they
will be instantiated as different objects and won't interfere between each other.

As an example, see [Archan's own configuration file][archan-conf].

[archan-conf]: https://github.com/Genida/archan/blob/master/config/archan.yml

To get the list of available plugins in your current environment,
run `archan --list-plugins` or `archan -l`.

## Writing a plugin

### Plugin discovery

You can write three types of plugins: analyzers, providers and checkers.
Your plugin does not need to be in an installable package. All it needs to
be summoned is to be available in your current Python path. However, if you want
it to be automatically discovered by Archan, you will have to make it installable,
through pip or simply `python setup.py install` command or equivalent.

If you decide to write a Python package for your plugin, I recommend you
to name it `archan-your-plugin` for consistency. If you plan to make it live
along other code in an already existing package, just leave the name as it is.

To make your plugin discoverable by Archan, use the `archan` entry point
in your `setup.py`:

```python

from setuptools import setup

setup(
    ...,
    'entry_points': {
        'archan': [
            'mypackage.MyPlugin = mypackage.mymodule:MyPlugin',
        ]
    }
```

If you build your package with Poetry, use this instead:

```toml
[tool.poetry.plugins.archan]
"mypackage.MyPlugin" = "mkdocstrings.plugin:MkdocstringsPlugin"
```

The name of the entry point should by convention be composed of the name of
your package in lower case, a dot, and the name of the Python class, though
you can name it whatever you want. Remember that this name will be the one
used in the configuration file.

Also a good thing is to make the plugin importable thanks to its name only:

```python
import mypackage.MyPlugin
```

But again, this is just a convention.

### Plugin class

You can write three types of plugins: analyzers, providers and checkers.
For each of them, you have to inherit from its corresponding class:

```python
from archan import Analyzer, Provider, Checker

class MyAnalyzer(Analyzer): ...
class MyProvider(Provider): ...
class MyChecker(Checker): ...
```

A provider or checker plugin must have the following class attributes:

- identifier: the identifier of the plugin. It must be the same name as in
  your entry points, so that displaying its help tells how to summon it.
- name: the verbose name of the plugin.
- description: a description to explain what it does.
- (optional) arguments: a tuple/list of Argument instances. This one is only
  used to display some help for the plugin. An argument is composed of a name,
  a type, a description and a default value.

```python
from archan import Provider, Argument

class MyProvider(Provider):
    identifier = 'mypackage.MyProvider'
    name = 'This is my Provider'
    description = """
    Don't hesitate to use multi-line strings as the lines will be de-indented,
    concatenated again and wrapped to match the console width.

    Blank lines will be kept though, so the above line will not be removed.
    """

    arguments = (
        Argument('my_arg', int, 'This argument is useful.', 42),
        # don't forget the ending comma if you have just one   ^   argument
    )
```

Additionally, a checker plugin should have the `hint` class attribute (string).
The hint describe what you should do if the check fails.

For now, the analyzers plugins just have the `providers` and `checkers`
class attributes.

### Plugin methods

A provider must implement the `get_dsm(self, **kwargs)` method. This method
must return an instance of `DSM`. A DSM is composed of a two-dimensions
array, the matrix, a list of strings, the keys or names for each line/column
of the matrix, and optionally the categories for each key (a list of same size).

```python
from archan import DSM, Provider

class MyProvider(Provider):
    name = 'mypackage.MyProvider'

    def get_dsm(self, my_arg=42, **kwargs):
        # this is where you compute your stuff
        matrix_data = [...]
        entities = [...]
        categories = [...] or None
        # and return a DSM instance
        return DSM(matrix_data, entities, categories)
```

A checker must implement the `check(self, dsm, **kwargs)` method.

```python
from archan import DSM, Checker

class MyChecker(Checker):
    name = 'mypackage.MyChecker'

    def check(self, dsm, **kwargs):
        # this is where you check your stuff
        # with dsm.data, dsm.entities, dsm.categories, dsm.size (rows, columns)
        ...
        # and return True, False, or a constant from Checker: PASSED or FAILED
        # with an optional message
        return Checker.FAILED, 'too much issues in module XXX'
```

### Logging messages

Each plugin instance has a `logger` attribute available. Use it to log
messages with `self.logger.debug`, `info`, `warning`, `error` or
`critical`.

## Available plugins

Here is the list of plugins available in other packages.

See other plugins published to PyPi by searching for
["archan-"](https://pypi.org/search/?q=archan-)

### Providers

- `dependenpy.InternalDependencies`: Provide matrix data about internal
  dependencies in a set of packages. Install it with `pip install dependenpy`.
