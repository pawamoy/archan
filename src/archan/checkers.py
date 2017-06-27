# -*- coding: utf-8 -*-

"""Checker module."""

from colorama import Back, Fore, Style

from .errors import DSMError
from .utils import Argument, Logger, pretty_description


# TODO: also add some "expect" attribute to describe the expected data format
class Checker(object):
    """
    Checker class.

    An instance of Checker implements a check method that analyzes an instance
    of DSM and return a true or false value, with optional message.
    """

    identifier = 'archan.AbstractChecker'
    name = 'Generic checker'
    description = ''
    hint = ''
    arguments = ()

    PASSED = 1
    FAILED = 0
    IGNORED = -1
    NOT_IMPLEMENTED = -2

    STATUS = (PASSED, FAILED, IGNORED, NOT_IMPLEMENTED)

    @classmethod
    def get_help(cls):
        """Return a help text for the current subclass of Checker."""
        return (
            '{bold}Identifier:{none} {blue}{identifier}{none}\n'
            '{bold}Name:{none} {name}\n'
            '{bold}Description:{none}\n{description}\n' +
            ('{bold}Arguments:{none}\n{arguments}\n' if cls.arguments else '')
        ).format(
            bold=Style.BRIGHT,
            blue=Back.BLUE + Fore.WHITE,
            none=Style.RESET_ALL,
            identifier=cls.identifier,
            name=cls.name,
            description=pretty_description(cls.description, indent=2),
            arguments='\n'.join([a.help for a in cls.arguments])
        )

    def __init__(self, ignore=False, **run_kwargs):
        """
        Initialization method.

        Args:
            ignore (bool): still pass if failed or not.
            **run_kwargs: arguments passed to the check method when run.
        """
        self.logger = Logger.get_logger(__name__)
        self.ignore = ignore
        self.run_kwargs = run_kwargs
        self.result = None

    @property
    def help(self):
        """Property to return the help text for a checker."""
        return self.__class__.get_help()

    def check(self, dsm, **kwargs):
        """
        Check the DSM and return a result.

        Args:
            dsm (DSM): DSM instance to check.
            **kwargs: additional arguments.

        Returns:
            obj: Checker constant or object with a ``__bool__`` method.
        """
        raise NotImplementedError

    def run(self, dsm):
        """
        Run the check method and format the result for analyzers.

        Args:
            dsm (DSM): DSM instance to check.

        Returns:
            int, str: status constant from Checker class and messages.
        """
        try:
            result = self.check(dsm, **self.run_kwargs)
            messages = ''
            if isinstance(result, tuple):
                result, messages = result

            if result not in Checker.STATUS:
                result = Checker.PASSED if bool(result) else Checker.FAILED

            if result == Checker.FAILED and self.ignore:
                result = Checker.IGNORED

            return result, messages
        except NotImplementedError:
            return Checker.NOT_IMPLEMENTED, ''


class CompleteMediation(Checker):
    """Complete mediation check."""

    identifier = 'archan.CompleteMediation'
    name = 'Complete Mediation'
    description = """
    Every access to every object must be checked for authority.
    This principle, when systematically applied, is the primary underpinning
    of the protection system. It forces a system-wide view of access control,
    which in addition to normal operation includes initialization, recovery,
    shutdown, and maintenance. It implies that a foolproof method of
    identifying the source of every request must be devised. It also requires
    that proposals to gain performance by remembering the result of an
    authority check be examined skeptically. If a change in authority occurs,
    such remembered results must be systematically updated."""
    hint = 'Remove the dependencies or deviate them through a broker module.'

    @staticmethod
    def generate_mediation_matrix(dsm):
        """
        Generate the mediation matrix of the given matrix.

        Rules for mediation matrix generation:

        Set -1 for items NOT to be considered
        Set 0 for items which MUST NOT be present
        Set 1 for items which MUST be present

        Each module has optional dependencies to itself.

        - Framework has optional dependency to all framework items (-1),
          and to nothing else.
        - Core libraries have dependencies to framework.
          Dependencies to other core libraries are tolerated.
        - Application libraries have dependencies to framework.
          Dependencies to other core or application libraries are tolerated.
          No dependencies to application modules.
        - Application modules have dependencies to framework and libraries.
          Dependencies to other application modules
          should be mediated over a broker.
          Dependencies to data are tolerated.
        - Data have no dependencies at all
          (but framework/libraries would be tolerated).

        Args:
            dsm (:class:`DesignStructureMatrix`): the DSM to generate
                the mediation matrix for.
        """
        cat = dsm.categories
        ent = dsm.entities
        size = dsm.size[0]

        if not cat:
            cat = ['appmodule'] * size

        packages = [e.split('.')[0] for e in ent]

        # define and initialize the mediation matrix
        mediation_matrix = [[0 for _ in range(size)]
                            for _ in range(size)]

        for i in range(0, size):
            for j in range(0, size):
                if cat[i] == 'framework':
                    if cat[j] == 'framework':
                        mediation_matrix[i][j] = -1
                    else:
                        mediation_matrix[i][j] = 0
                elif cat[i] == 'corelib':
                    if (cat[j] in ('framework', 'corelib') or
                            ent[i].startswith(packages[j] + '.') or
                            i == j):
                        mediation_matrix[i][j] = -1
                    else:
                        mediation_matrix[i][j] = 0
                elif cat[i] == 'applib':
                    if (cat[j] in ('framework', 'corelib', 'applib') or
                            ent[i].startswith(packages[j] + '.') or
                            i == j):
                        mediation_matrix[i][j] = -1
                    else:
                        mediation_matrix[i][j] = 0
                elif cat[i] == 'appmodule':
                    # we cannot force an app module to import things from
                    # the broker if the broker itself did not import anything
                    if (cat[j] in ('framework', 'corelib',
                                   'applib', 'broker', 'data') or
                            ent[i].startswith(packages[j] + '.') or
                            i == j):
                        mediation_matrix[i][j] = -1
                    else:
                        mediation_matrix[i][j] = 0
                elif cat[i] == 'broker':
                    # we cannot force the broker to import things from
                    # app modules if there is nothing to be imported.
                    # also broker should be authorized to use third apps
                    if (cat[j] in (
                            'appmodule', 'corelib', 'framework') or
                            ent[i].startswith(packages[j] + '.') or
                            i == j):
                        mediation_matrix[i][j] = -1
                    else:
                        mediation_matrix[i][j] = 0
                elif cat[i] == 'data':
                    if (cat[j] == 'framework' or
                            i == j):
                        mediation_matrix[i][j] = -1
                    else:
                        mediation_matrix[i][j] = 0
                else:
                    # mediation_matrix[i][j] = -2  # errors in the generation
                    raise DSMError(
                        'Mediation matrix value NOT generated for %s:%s' % (
                            i, j))

        return mediation_matrix

    @staticmethod
    def matrices_compliance(dsm, complete_mediation_matrix):
        """
        Check if matrix and its mediation matrix are compliant.

        Args:
            dsm (:class:`DesignStructureMatrix`): the DSM to check.
            complete_mediation_matrix (list of list of int): 2-dim array

        Returns:
            bool: True if compliant, else False
        """
        matrix = dsm.data
        rows_dep_matrix = len(matrix)
        cols_dep_matrix = len(matrix[0])
        rows_med_matrix = len(complete_mediation_matrix)
        cols_med_matrix = len(complete_mediation_matrix[0])

        if (rows_dep_matrix != rows_med_matrix or
                cols_dep_matrix != cols_med_matrix):
            raise DSMError('Matrices are NOT compliant '
                           '(number of rows/columns not equal)')

        discrepancy_found = False
        message = []
        for i in range(0, rows_dep_matrix):
            for j in range(0, cols_dep_matrix):
                if ((complete_mediation_matrix[i][j] == 0 and
                        matrix[i][j] > 0) or
                        (complete_mediation_matrix[i][j] == 1 and
                         matrix[i][j] < 1)):
                    discrepancy_found = True
                    message.append(
                        'Untolerated dependency at %s:%s (%s:%s): '
                        '%s instead of %s' % (
                            i, j, dsm.entities[i], dsm.entities[j],
                            matrix[i][j], complete_mediation_matrix[i][j]))

        message = '\n'.join(message)

        return not discrepancy_found, message

    def check(self, dsm, **kwargs):
        """
        Check if matrix and its mediation matrix are compliant.

        It means that number of dependencies for each (line, column) is either
        0 if the mediation matrix (line, column) is 0, or >0 if the mediation
        matrix (line, column) is 1.

        Args:
            dsm (:class:`DesignStructureMatrix`): the DSM to check.

        Returns:
            bool: True if compliant, else False
        """
        # generate complete_mediation_matrix according to each category
        med_matrix = CompleteMediation.generate_mediation_matrix(dsm)
        return CompleteMediation.matrices_compliance(dsm, med_matrix)


class EconomyOfMechanism(Checker):
    """Economy of mechanism check."""

    identifier = 'archan.EconomyOfMechanism'
    name = 'Economy of Mechanism'
    hint = 'Reduce the number of dependencies in your own code ' \
           'or increase the simplicity factor.'
    description = """
    Keep the design as simple and small as possible. This well-known principle
    applies to any aspect of a system, but it deserves emphasis for protection
    mechanisms for this reason: design and implementation errors that result in
    unwanted access paths will not be noticed during normal use (since normal
    use usually does not include attempts to exercise improper access paths).
    As a result, techniques such as line-by-line inspection of software and
    physical examination of hardware that implements protection mechanisms are
    necessary. For such techniques to be successful, a small and simple design
    is essential."""

    arguments = (
        Argument('simplicity_factor', int,
                 'If the number of cells with dependencies in the DSM '
                 'is lower than the DSM size multiplied by the simplicity '
                 'factor, then this criterion is verified.', 2),
    )

    def check(self, dsm, simplicity_factor=2, **kwargs):
        """
        Check economy of mechanism.

        As first abstraction, number of dependencies between two modules
        < 2 * the number of modules
        (dependencies to the framework are NOT considered).

        Args:
            dsm (:class:`DesignStructureMatrix`): the DSM to check.
            simplicity_factor (int): simplicity factor.

        Returns:
            bool: True if economic, else False
        """
        # economy_of_mechanism
        economy_of_mechanism = False
        message = ''
        data = dsm.data
        categories = dsm.categories
        dsm_size = dsm.size[0]

        if not categories:
            categories = ['appmodule'] * dsm_size

        dependency_number = 0
        # evaluate Matrix(data)
        for i in range(0, dsm_size):
            for j in range(0, dsm_size):
                if (categories[i] not in ('framework', 'corelib') and
                        categories[j] not in ('framework', 'corelib') and
                        data[i][j] > 0):
                    dependency_number += 1
                    # check comparison result
        if dependency_number < dsm_size * simplicity_factor:
            economy_of_mechanism = True
        else:
            message = ' '.join([
                'Number of dependencies (%s)' % dependency_number,
                '> number of rows (%s)' % dsm_size,
                '* simplicity factor (%s) = %s' % (
                    simplicity_factor, dsm_size * simplicity_factor)])
        return economy_of_mechanism, message


class SeparationOfPrivileges(Checker):
    """Separation of privileges check."""

    identifier = 'archan.SeparationOfPrivileges'
    name = 'Separation of Privileges'
    description = """
    Where feasible, a protection mechanism that requires two keys to unlock it
    is more robust and flexible than one that allows access to the presenter of
    only a single key. The relevance of this observation to computer systems
    was pointed out by R. Needham in 1973. The reason is that, once the
    mechanism is locked, the two keys can be physically separated and distinct
    programs, organizations, or individuals made responsible for them. From
    then on, no single accident, deception, or breach of trust is sufficient to
    compromise the protected information. This principle is often used in bank
    safe-deposit boxes. It is also at work in the defense system that fires a
    nuclear weapon only if two different people both give the correct command.
    In a computer system, separated keys apply to any situation in which two or
    more conditions must be met before access should be permitted. For example,
    systems providing user-extendible protected data types usually depend on
    separation of privilege for their implementation."""
    # TODO: add hint

    def check(self, dsm, **kwargs):
        """TODO: To implement."""
        raise NotImplementedError


class LeastPrivileges(Checker):
    """Least privileges check."""

    identifier = 'archan.LeastPrivileges'
    name = 'Least Privileges'
    description = """
    Every program and every user of the system should operate using the least
    set of privileges necessary to complete the job. Primarily, this principle
    limits the damage that can result from an accident or error. It also
    reduces the number of potential interactions among privileged programs to
    the minimum for correct operation, so that unintentional, unwanted, or
    improper uses of privilege are less likely to occur. Thus, if a question
    arises related to misuse of a privilege, the number of programs that must
    be audited is minimized. Put another way, if a mechanism can provide
    "firewalls," the principle of least privilege provides a rationale for
    where to install the firewalls. The military security rule of
    "need-to-know" is an example of this principle."""
    # TODO: add hint

    def check(self, dsm, **kwargs):
        """TODO: To implement."""
        raise NotImplementedError


class LeastCommonMechanism(Checker):
    """Least common mechanism check."""

    identifier = 'archan.LeastCommonMechanism'
    name = 'Least Common Mechanism'
    hint = 'Reduce number of modules having dependencies to the listed module.'
    description = """
    Minimize the amount of mechanism common to more than one user and depended
    on by all users. Every shared mechanism (especially one involving shared
    variables) represents a potential information path between users and must
    be designed with great care to be sure it does not unintentionally
    compromise security. Further, any mechanism serving all users must be
    certified to the satisfaction of every user, a job presumably harder than
    satisfying only one or a few users. For example, given the choice of
    implementing a new function as a supervisor procedure shared by all users
    or as a library procedure that can be handled as though it were the user's
    own, choose the latter course. Then, if one or a few users are not
    satisfied with the level of certification of the function, they can provide
    a substitute or not use it at all. Either way, they can avoid being harmed
    by a mistake in it."""

    arguments = (
        Argument('independence_factor', int,
                 'If the maximum dependencies for one module is inferior or '
                 'equal to the DSM size divided by the independence factor, '
                 'then this criterion is verified.', 5),
    )

    def check(self, dsm, independence_factor=5, **kwargs):
        """
        Check least common mechanism.

        Args:
            dsm (:class:`DesignStructureMatrix`): the DSM to check.
            independence_factor (int): if the maximum dependencies for one
                module is inferior or equal to the DSM size divided by the
                independence factor, then this criterion is verified.

        Returns:
            bool: True if least common mechanism, else False
        """
        # leastCommonMechanismMatrix
        least_common_mechanism = False
        message = ''
        # get the list of dependent modules for each module
        data = dsm.data
        categories = dsm.categories
        dsm_size = dsm.size[0]

        if not categories:
            categories = ['appmodule'] * dsm_size

        dependent_module_number = []
        # evaluate Matrix(data)
        for j in range(0, dsm_size):
            dependent_module_number.append(0)
            for i in range(0, dsm_size):
                if (categories[i] != 'framework' and
                        categories[j] != 'framework' and
                        data[i][j] > 0):
                    dependent_module_number[j] += 1
        # except for the broker if any  and libs, check that threshold is not
        # overlapped
        #  index of brokers
        #  and app_libs are set to 0
        for index, item in enumerate(dsm.categories):
            if item == 'broker' or item == 'applib':
                dependent_module_number[index] = 0
        if max(dependent_module_number) <= dsm_size / independence_factor:
            least_common_mechanism = True
        else:
            maximum = max(dependent_module_number)
            message = (
                'Dependencies to %s (%s) > matrix size (%s) / '
                'independence factor (%s) = %s' % (
                    dsm.entities[dependent_module_number.index(maximum)],
                    maximum, dsm_size, independence_factor,
                    dsm_size / independence_factor))

        return least_common_mechanism, message


class LayeredArchitecture(Checker):
    """
    Layered architecture check.

    Check that the DSM can be diagonalized (no marks in upper right or
    lower left corner).
    """

    identifier = 'archan.LayeredArchitecture'
    name = 'Layered Architecture'
    description = """
    The modules that are part of the project should be organized in a layered
    way by means of groups. Modules like frameworks and librairies should be
    put first, then other components like the main features of the project.
    Security and data modules should be put last. A well layered architecture
    should be visible in the form of a matrix which has dependencies into only
    one corner (for example: in the lower-left part)."""
    hint = 'Ensure that your applications are listed in the right ' \
           'order when building the DSM, or remove dependencies.'

    def check(self, dsm, **kwargs):
        """
        Check layered architecture.

        Args:
            dsm (:class:`DesignStructureMatrix`): the DSM to check.

        Returns:
            bool: True if layered architecture, else False
        """
        layered_architecture = True
        messages = []
        categories = dsm.categories
        dsm_size = dsm.size[0]

        if not categories:
            categories = ['appmodule'] * dsm_size

        for i in range(0, dsm_size - 1):
            for j in range(i + 1, dsm_size):
                if (categories[i] != 'broker' and
                        categories[j] != 'broker' and
                        dsm.entities[i].split('.')[0] != dsm.entities[j].split('.')[0]):  # noqa
                    if dsm.data[i][j] > 0:
                        layered_architecture = False
                        messages.append(
                            'Dependency from %s to %s breaks the '
                            'layered architecture.' % (
                                dsm.entities[i], dsm.entities[j]))

        return layered_architecture, '\n'.join(messages)


class OpenDesign(Checker):
    """
    Open design check.

    Simply take an argument to say if it should pass or not.
    """

    identifier = 'archan.OpenDesign'
    name = 'Open Design'
    description = """
    The design should not be secret. The mechanisms should not depend on the
    ignorance of potential attackers, but rather on the possession of specific,
    more easily protected, keys or passwords. This decoupling of protection
    mechanisms from protection keys permits the mechanisms to be examined by
    many reviewers without concern that the review may itself compromise the
    safeguards. In addition, any skeptical user may be allowed to convince
    himself that the system he is about to use is adequate for his purpose.
    Finally, it is simply not realistic to attempt to maintain secrecy for any
    system which receives wide distribution."""
    # TODO: add hint

    arguments = (
        Argument('ok', bool,
                 'Since Open Design computes nothing, you need to tell '
                 'it if the check should succeed or not.', False),
    )

    def check(self, dsm, ok=False, **kwargs):
        """Return False by default, argument ``ok`` otherwise."""
        return ok


class CodeClean(Checker):
    """
    Code clean checker.

    Check that the number of issues per file and per line of code is below
    a certain value. Also check for number of similarities between files.
    """

    identifier = 'archan.CodeClean'
    name = 'Code Clean'
    description = """
    The code base should be kept coherent and consistent. Complexity of
    functions must not be too important. Conventions and standards must be used
    in order to maintain a very human readable and maintainable code."""
    # TODO: add hint

    def check(self, dsm, **kwargs):
        """TODO: To implement."""
        raise NotImplementedError
