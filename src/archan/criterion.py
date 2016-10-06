# -*- coding: utf-8 -*-

# Copyright (c) 2015 Timothée Mazzucotelli
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

from __future__ import unicode_literals
import os
import archan
from archan.errors import ArchanError


def read_criterion(criterion, folder=None):
    if folder:
        paper_dir = folder
    else:
        paper_dir = os.path.abspath(
            os.path.join(os.path.dirname(archan.__file__), 'criteria'))
    try:
        with open(os.path.join(paper_dir, criterion + '.txt')) as f:
            return f.read()
    except IOError:
        return ''


class Criterion(object):
    FAILED = 0
    PASSED = 1
    NOT_IMPLEMENTED = -1
    IGNORED = -2

    def __init__(self, codename, title, description='',
                 hint='', check=None, **kwargs):
        self.codename = codename
        self.title = title
        self.description = description
        self.hint = hint
        if check:
            self.check = check
        self.kwargs = kwargs

    def __call__(self, *args, **kwargs):
        kwargs.update(self.kwargs)
        if hasattr(self, 'check') and callable(self.check):
            success, message = self.check(*args, **kwargs)
            if success:
                return Criterion.PASSED, message
            return Criterion.FAILED, message
        return Criterion.NOT_IMPLEMENTED, ''


def _generate_mediation_matrix(dsm):
    """Generate the mediation matrix of the given matrix.

    Rules for mediation matrix generation:

    Set -1 for items NOT to be considered
    Set 0 for items which MUST NOT be present
    Set 1 for items which MUST be present

    Each module has optional dependencies to itself.

    - Framework has optional dependency to all framework items (-1),
      and to nothing else.
    - Core libs have dependencies to framework.
      Dependencies to other core libs are tolerated.
    - Application libs have dependencies to framework.
      Dependencies to other core or application libs are tolerated.
      No dependencies to application modules.
    - Application modules have dependencies to framework and libs.
      Dependencies to other application modules
      should be mediated over a broker.
      Dependencies to data are tolerated.
    - Data have no dependencies at all
      (but framework/libs would be tolerated).

    """

    cat = dsm.categories
    ent = dsm.entities
    size = dsm.size
    packages = [e.split('.')[0] for e in ent]

    # define and initialize the mediation matrix
    mediation_matrix = [[0 for _ in range(size)]
                        for _ in range(size)]

    for i in range(0, size):
        for j in range(0, size):
            if cat[i] == dsm.framework:
                if cat[j] == dsm.framework:
                    mediation_matrix[i][j] = -1
                else:
                    mediation_matrix[i][j] = 0
            elif cat[i] == dsm.core_lib:
                if (cat[j] in (dsm.framework, dsm.core_lib) or
                        ent[i].startswith(packages[j] + '.') or
                        i == j):
                    mediation_matrix[i][j] = -1
                else:
                    mediation_matrix[i][j] = 0
            elif cat[i] == dsm.app_lib:
                if (cat[j] in (dsm.framework, dsm.core_lib, dsm.app_lib) or
                        ent[i].startswith(packages[j] + '.') or
                        i == j):
                    mediation_matrix[i][j] = -1
                else:
                    mediation_matrix[i][j] = 0
            elif cat[i] == dsm.app_module:
                # we cannot force an app module to import things from
                # the broker if the broker itself did not import anything
                if (cat[j] in (dsm.framework, dsm.core_lib,
                               dsm.app_lib, dsm.broker, dsm.data) or
                        ent[i].startswith(packages[j] + '.') or
                        i == j):
                    mediation_matrix[i][j] = -1
                else:
                    mediation_matrix[i][j] = 0
            elif cat[i] == dsm.broker:
                # we cannot force the broker to import things from
                # app modules if there is nothing to be imported.
                # also broker should be authorized to use third apps
                if (cat[j] in (dsm.app_module, dsm.core_lib, dsm.framework) or
                        ent[i].startswith(packages[j] + '.') or
                        i == j):
                    mediation_matrix[i][j] = -1
                else:
                    mediation_matrix[i][j] = 0
            elif cat[i] == dsm.data:
                if (cat[j] == dsm.framework or
                        i == j):
                    mediation_matrix[i][j] = -1
                else:
                    mediation_matrix[i][j] = 0
            else:
                # mediation_matrix[i][j] = -2  # errors in the generation
                raise ArchanError(
                    'Mediation matrix value NOT generated for %s:%s' % (
                        i, j))

    return mediation_matrix


def _matrices_compliance(dsm, complete_mediation_matrix):
    """Check if matrix and its mediation matrix are compliant.

    :type dsm: :class:`DesignStructureMatrix`
    :param dsm: matrix to check
    :type complete_mediation_matrix: list of list of int
    :param complete_mediation_matrix: 2-dim array (mediation matrix)
    :return: bool, True if compliant, else False
    """

    matrix = dsm.dependency_matrix
    rows_dep_matrix = len(matrix)
    cols_dep_matrix = len(matrix[0])
    rows_med_matrix = len(complete_mediation_matrix)
    cols_med_matrix = len(complete_mediation_matrix[0])

    if (rows_dep_matrix != rows_med_matrix or
            cols_dep_matrix != cols_med_matrix):
        raise ArchanError('Matrices are NOT compliant '
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
                    '  Untolerated dependency at %s:%s (%s:%s): '
                    '%s instead of %s' % (
                        i, j, dsm.entities[i], dsm.entities[j],
                        matrix[i][j], complete_mediation_matrix[i][j]))

    message = '\n'.join(message)

    return not discrepancy_found, message


def check_complete_mediation(dsm):
    """Check if matrix and its mediation matrix are compliant, meaning
    that number of dependencies for each (line, column) is either 0 if
    the mediation matrix (line, column) is 0, or >0 if the mediation matrix
    (line, column) is 1.

    :type dsm: :class:`DesignStructureMatrix`
    :param dsm: matrix to check
    :return: bool, True if compliant, else False
    """

    # generate complete_mediation_matrix according to each category
    med_matrix = _generate_mediation_matrix(dsm)
    matrices_compliant = _matrices_compliance(dsm, med_matrix)
    # check comparison result
    return matrices_compliant


def check_economy_of_mechanism(dsm, simplicity_factor=2):
    """Check economy of mechanism.

    As first abstraction, number of dependencies between two modules
    < 2 * the number of modules
    (dependencies to the framework are NOT considered).

    :type dsm: :class:`DesignStructureMatrix`
    :param dsm: matrix to check
    :return: bool, True if economic, else False
    """

    # economy_of_mechanism
    economy_of_mechanism = False
    message = ''
    dependency_matrix = dsm.dependency_matrix
    categories = dsm.categories
    dsm_size = dsm.size

    dependency_number = 0
    # evaluate Matrix(dependency_matrix)
    for i in range(0, dsm_size):
        for j in range(0, dsm_size):
            if (categories[i] not in (dsm.framework, dsm.core_lib) and
                    categories[j] not in (dsm.framework, dsm.core_lib) and
                    dependency_matrix[i][j] > 0):
                dependency_number += 1
                # check comparison result
    if dependency_number < dsm_size * simplicity_factor:
        economy_of_mechanism = True
    else:
        message = ' '.join([
            '  Number of dependencies (%s)' % dependency_number,
            '> number of rows (%s)' % dsm_size,
            '* simplicity factor (%s) = %s' % (
                simplicity_factor, dsm_size * simplicity_factor)])
    return economy_of_mechanism, message


def check_least_common_mechanism(dsm, independence_factor=5):
    """Check least common mechanism.

    :type dsm: :class:`DesignStructureMatrix`
    :param dsm: matrix to check
    :return: bool
    """

    # leastCommonMechanismMatrix
    least_common_mechanism = False
    message = ''
    # get the list of dependent modules for each module
    dependency_matrix = dsm.dependency_matrix
    categories = dsm.categories
    dsm_size = dsm.size

    dependent_module_number = []
    # evaluate Matrix(dependency_matrix)
    for j in range(0, dsm_size):
        dependent_module_number.append(0)
        for i in range(0, dsm_size):
            if (categories[i] != dsm.framework and
                    categories[j] != dsm.framework and
                    dependency_matrix[i][j] > 0):
                dependent_module_number[j] += 1
    # except for the broker if any  and libs, check that threshold is not
    # overlapped
    #  index of brokers
    #  and app_libs are set to 0
    for index, item in enumerate(dsm.categories):
        if item == dsm.broker or item == dsm.app_lib:
            dependent_module_number[index] = 0
    if max(dependent_module_number) <= dsm.size / independence_factor:
        least_common_mechanism = True
    else:
        maximum = max(dependent_module_number)
        message = ('  Dependencies to %s (%s) '
                   '> matrix size (%s) / independence factor (%s) = %s' % (
                       dsm.entities[dependent_module_number.index(maximum)],
                       maximum, dsm.size, independence_factor,
                       dsm.size / independence_factor))

    return least_common_mechanism, message


def check_layered_architecture(dsm):
    """Check layered architecture.

    :type dsm: :class:`DesignStructureMatrix`
    :param dsm: matrix to check
    :return: bool
    """

    layered_architecture = True
    messages = []
    for i in range(0, dsm.size - 1):
        for j in range(i + 1, dsm.size):
            if (dsm.categories[i] != dsm.broker and
                    dsm.categories[j] != dsm.broker and
                    (dsm.entities[i].split('.')[0] !=
                        dsm.entities[j].split('.')[0])):
                if dsm.dependency_matrix[i][j] > 0:
                    layered_architecture = False
                    messages.append(
                        '  Dependency from %s to %s breaks the '
                        'layered architecture.' % (
                            dsm.entities[i], dsm.entities[j]))

    return layered_architecture, '\n'.join(messages)


COMPLETE_MEDIATION = Criterion(
    'COMPLETE_MEDIATION', 'Complete Mediation',
    description=read_criterion('complete_mediation'),
    check=check_complete_mediation,
    hint='Remove the dependencies or deviate them through a broker module.')
ECONOMY_OF_MECHANISM = Criterion(
    'ECONOMY_OF_MECHANISM', 'Economy Of Mechanism',
    description=read_criterion('economy_of_mechanism'),
    check=check_economy_of_mechanism,
    hint='Reduce the number of dependencies in your own code '
         'or increase the simplicity factor.',
    simplicity_factor=2)
SEPARATION_OF_PRIVILEGES = Criterion(
    'SEPARATION_OF_PRIVILEGES', 'Separation Of Privileges',
    description=read_criterion('separation_of_privileges'))
LEAST_PRIVILEGES = Criterion(
    'LEAST_PRIVILEGES', 'Least Privileges',
    description=read_criterion('least_privileges'))
LEAST_COMMON_MECHANISM = Criterion(
    'LEAST_COMMON_MECHANISM', 'Least Common Mechanism',
    description=read_criterion('least_common_mechanism'),
    check=check_least_common_mechanism,
    hint='Reduce number of modules having dependencies to the listed module.',
    independence_factor=5)
LAYERED_ARCHITECTURE = Criterion(
    'LAYERED_ARCHITECTURE', 'Layered Architecture',
    description=read_criterion('layered_architecture'),
    check=check_layered_architecture,
    hint='Ensure that your applications are listed in the right '
         'order when building the DSM, or remove dependencies.')
OPEN_DESIGN = Criterion(
    'OPEN_DESIGN', 'Open Design',
    description=read_criterion('open_design'))
CODE_CLEAN = Criterion(
    'CODE_CLEAN', 'Code Clean',
    description=read_criterion('code_clean'))

CRITERIA = [
    COMPLETE_MEDIATION,
    ECONOMY_OF_MECHANISM,
    SEPARATION_OF_PRIVILEGES,
    LEAST_PRIVILEGES,
    LEAST_COMMON_MECHANISM,
    LAYERED_ARCHITECTURE,
    OPEN_DESIGN,
    CODE_CLEAN
]
