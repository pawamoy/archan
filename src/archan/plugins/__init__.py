"""Plugins submodule."""

from collections import namedtuple
from typing import Optional, Sequence

from archan.enums import ResultCode
from archan.logging import Logger
from archan.printing import PrintableArgumentMixin, PrintableNameMixin, PrintablePluginMixin

logger = Logger.get_logger(__name__)


class Argument(PrintableArgumentMixin):
    """Placeholder for name, class, description and default value."""

    def __init__(self, name, cls, description, default=None):
        """Initialization method.

        Arguments:
            name (str): name of the argument.
            cls (type): type of the argument.
            description (str): description of the argument.
            default (obj): default value for the argument.
        """
        self.name = name
        self.cls = cls
        self.description = description
        self.default = default

    def __str__(self):
        return f"  {self.name} ({self.cls}, default {self.default}): {self.description}"


# TODO: also add some "expect" attribute to describe the expected data format
class Checker(PrintableNameMixin, PrintablePluginMixin):
    """Checker class.

    An instance of Checker implements a check method that analyzes an instance
    of DSM/DMM/MDM and return a true or false value, with optional message.
    """

    identifier = ""
    name = ""
    description = ""
    hint = ""
    argument_list: Sequence[Argument] = ()

    Code = ResultCode

    def __init__(
        self,
        name: Optional[str] = None,
        description: Optional[str] = None,
        hint: Optional[str] = None,
        allow_failure: bool = False,
        passes: Optional[str] = None,
        arguments=None,
    ):
        """Initialization method.

        Arguments:
            name: The checker name.
            description: The checker description.
            hint: Hint provided for failures.
            allow_failure: Still pass if failed or not.
            passes: ???
            arguments: Arguments passed to the check method when run.
        """
        if name:
            self.name = name
        if description:
            self.description = description
        if hint:
            self.hint = hint

        self.allow_failure = allow_failure
        self.passes = passes
        self.arguments = arguments or {}
        self.result = None

    def check(self, data, **kwargs):
        """Check the data and return a result.

        Arguments:
            data (DSM/DMM/MDM): DSM/DMM/MDM instance to check.
            **kwargs: additional arguments.

        Returns:
            obj: Checker constant or object with a ``__bool__`` method.
            tuple (obj, str): obj as before and string of messages
        """
        raise NotImplementedError

    def run(self, data):
        """Run the check method and format the result for analysis.

        Arguments:
            data (DSM/DMM/MDM): DSM/DMM/MDM instance to check.
        """
        result_type = namedtuple("Result", "code messages")

        if self.passes is True:
            result = result_type(Checker.Code.PASSED, "")
        elif self.passes is False:
            result = (
                result_type(Checker.Code.IGNORED, "") if self.allow_failure else result_type(Checker.Code.FAILED, "")
            )
        else:
            try:
                result = self.check(data, **self.arguments)
            except NotImplementedError:
                result = result_type(Checker.Code.NOT_IMPLEMENTED, "")
            else:
                messages = ""
                if isinstance(result, tuple):
                    result, messages = result

                if result not in Checker.Code:
                    result = Checker.Code.PASSED if bool(result) else Checker.Code.FAILED

                if result == Checker.Code.FAILED and self.allow_failure:
                    result = Checker.Code.IGNORED

                result = result_type(result, messages)
        self.result = result


class Provider(PrintableNameMixin, PrintablePluginMixin):
    """Provider class.

    An instance of provider implements a get_data method that returns an
    instance of DSM/DMM/MDM to be checked by an instance of Checker.
    """

    identifier = ""
    name = ""
    description = ""
    argument_list = ()

    def __init__(self, name: Optional[str] = None, description: Optional[str] = None, arguments=None):
        """Initialization method.

        Arguments:
            name: The provider name.
            description: The provider description.
            arguments (dict): arguments that will be used for get_data method.
        """
        if name:
            self.name = name
        if description:
            self.description = description

        self.arguments = arguments or {}
        self.data = None

    def get_data(self, **kwargs):
        """Abstract method. Return instance of DSM/DMM/MDM.

        Arguments:
            **kwargs: Keyword arguments.

        Raises:
            NotImplementedError: This method must be implemented in subclasses.
        """
        raise NotImplementedError

    def run(self):
        """Run the get_data method with run arguments, store the result."""
        self.data = self.get_data(**self.arguments)
