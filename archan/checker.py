# -*- coding: utf-8 -*-

# Copyright (c) 2015 Pierre Parrend
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Created on 8 janv. 2015

@author: Pierre.Parrend
"""

from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals
from builtins import range
from builtins import object
from past.utils import old_div

from archan.dsm import DesignStructureMatrix
from archan.errors import ArchanError


class Archan(object):
    """Architecture analyser class."""

    COMPLETE_MEDIATION = 1
    ECONOMY_OF_MECHANISM = 2
    SEPARATION_OF_PRIVILEGES = 4
    LEAST_PRIVILEGES = 8
    LEAST_COMMON_MECHANISM = 16
    LAYERED_ARCHITECTURE = 32
    OPEN_DESIGN = 64
    CODE_CLEAN = 128

    FAILED = 0
    PASSED = 1
    IGNORED = 2
    NOT_IMPLEMENTED = 3

    FLAGS = (
        COMPLETE_MEDIATION,
        ECONOMY_OF_MECHANISM,
        SEPARATION_OF_PRIVILEGES,
        LEAST_PRIVILEGES,
        LEAST_COMMON_MECHANISM,
        LAYERED_ARCHITECTURE,
        OPEN_DESIGN,
        CODE_CLEAN,
    )

    def __init__(self, dsm, flags=0,
                 simplicity_factor=2,
                 independence_factor=5):
        self.dsm = dsm
        self.flags = flags
        self.simplicity_factor = simplicity_factor
        self.independence_factor = independence_factor

    def flag_name(self, flag):
        if flag == Archan.COMPLETE_MEDIATION:
            return 'Complete Mediation'
        if flag == Archan.ECONOMY_OF_MECHANISM:
            return 'Economy of Mechanism'
        if flag == Archan.SEPARATION_OF_PRIVILEGES:
            return 'Separation Of Privileges'
        if flag == Archan.LEAST_PRIVILEGES:
            return 'Least Privileges'
        if flag == Archan.LEAST_COMMON_MECHANISM:
            return 'Least Common Mechanism'
        if flag == Archan.LAYERED_ARCHITECTURE:
            return 'Layered Architecture'
        if flag == Archan.OPEN_DESIGN:
            return 'Open Design'
        if flag == Archan.CODE_CLEAN:
            return 'Code Clean'

    def checker(self, flag):
        if flag == Archan.COMPLETE_MEDIATION:
            return self.complete_mediation
        if flag == Archan.ECONOMY_OF_MECHANISM:
            return self.economy_of_mechanism
        if flag == Archan.LEAST_COMMON_MECHANISM:
            return self.least_common_mechanism
        if flag == Archan.LAYERED_ARCHITECTURE:
            return self.layered_architecture
        if flag == Archan.OPEN_DESIGN:
            return self.open_design

        return lambda: Archan.NOT_IMPLEMENTED

    def check(self):
        return {
            flag:
                self.checker(flag)()
                if self.flags & flag
                else Archan.IGNORED
            for flag in Archan.FLAGS
        }

    # Rules for mediation matrix generation:
    #
    # Set -1 for items NOT to be considered
    # Set 0 for items which MUST NOT be present
    # Set 1 for items which MUST be present
    #
    # Each module has optional dependencies to itself.
    #
    # - Framework has optional dependency to all framework items (-1),
    #   and to nothing else.
    # - Core libs have dependencies to framework.
    #   Dependencies to other core libs are tolerated.
    # - Application libs have dependencies to framework.
    #   Dependencies to other core or application libs are tolerated.
    #   No dependencies to application modules.
    # - Application modules have dependencies to framework and libs.
    #   Dependencies to other application modules
    #   should be mediated over a broker.
    #   Dependencies to data are tolerated.
    # - Data have no dependencies at all
    #   (but framework/libs would be tolerated).
    def _generate_mediation_matrix(self):
        """Generate the mediation matrix of the given matrix."""

        cat = self.dsm.categories
        ent = self.dsm.entities
        size = self.dsm.size
        packages = [e.split('.')[0] for e in ent]

        # define and initialize the mediation matrix
        mediation_matrix = [[0 for _ in range(size)]
                            for _ in range(size)]

        for i in range(0, size):
            for j in range(0, size):
                if cat[i] == self.dsm.framework:
                    if cat[j] == self.dsm.framework:
                        mediation_matrix[i][j] = -1
                    else:
                        mediation_matrix[i][j] = 0
                elif cat[i] == self.dsm.core_lib:
                    if (cat[j] == self.dsm.framework or
                            cat[j] == self.dsm.core_lib or
                            ent[i].startswith(packages[j] + '.') or
                            i == j):
                        mediation_matrix[i][j] = -1
                    else:
                        mediation_matrix[i][j] = 0
                elif cat[i] == self.dsm.app_lib:
                    if (cat[j] == self.dsm.framework or
                            cat[j] == self.dsm.core_lib or
                            cat[j] == self.dsm.app_lib or
                            ent[i].startswith(packages[j] + '.') or
                            i == j):
                        mediation_matrix[i][j] = -1
                    else:
                        mediation_matrix[i][j] = 0
                elif cat[i] == self.dsm.app_module:
                    # we cannot force an app module to import things from
                    # the broker if the broker itself did not import anything
                    if (cat[j] == self.dsm.framework or
                            cat[j] == self.dsm.core_lib or
                            cat[j] == self.dsm.app_lib or
                            cat[j] == self.dsm.broker or
                            cat[j] == self.dsm.data or
                            ent[i].startswith(packages[j] + '.') or
                            i == j):
                        mediation_matrix[i][j] = -1
                    else:
                        mediation_matrix[i][j] = 0
                elif cat[i] == self.dsm.broker:
                    # we cannot force the broker to import things from
                    # app modules if there is nothing to be imported
                    if (cat[j] == self.dsm.app_module or
                            cat[j] == self.dsm.framework or
                            ent[i].startswith(packages[j] + '.') or
                            i == j):
                        mediation_matrix[i][j] = -1
                    else:
                        mediation_matrix[i][j] = 0
                elif cat[i] == self.dsm.data:
                    if (cat[j] == self.dsm.framework or
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

    def _matrices_compliance(self, complete_mediation_matrix):
        """Check if matrix and its mediation matrix are compliant.

        :type dsm: :class:`DesignStructureMatrix`
        :param dsm: matrix to check
        :type complete_mediation_matrix: list of list of int
        :param complete_mediation_matrix: 2-dim array (mediation matrix)
        :return: bool, True if compliant, else False
        """

        matrix = self.dsm.dependency_matrix
        rows_dep_matrix = len(matrix)
        cols_dep_matrix = len(matrix[0])
        rows_med_matrix = len(complete_mediation_matrix)
        cols_med_matrix = len(complete_mediation_matrix[0])

        if (rows_dep_matrix != rows_med_matrix or
                cols_dep_matrix != cols_med_matrix):
            print("Matrices are NOT compliant "
                  "(number of rows/columns not equal)")
            return False

        discrepancy_found = False
        for i in range(0, rows_dep_matrix):
            for j in range(0, cols_dep_matrix):
                if ((complete_mediation_matrix[i][j] == 0 and
                        matrix[i][j] > 0) or
                    (complete_mediation_matrix[i][j] == 1 and
                        matrix[i][j] < 1)):
                    discrepancy_found = True
                    print("Matrix discrepancy found "
                          "at %s:%s (%s:%s): %s/%s" % (
                              i, j, self.dsm.entities[i], self.dsm.entities[j],
                              complete_mediation_matrix[i][j],
                              matrix[i][j]))

        return not discrepancy_found

    def complete_mediation(self):
        """Check if matrix and its mediation matrix are compliant, meaning
        that number of dependencies for each (line, column) is either 0 if
        the mediation matrix (line, column) is 0, or >0 if the mediation matrix
        (line, column) is 1.

        :type dsm: :class:`DesignStructureMatrix`
        :param dsm: matrix to check
        :return: bool, True if compliant, else False
        """

        # generate complete_mediation_matrix according to each category
        med_matrix = Archan._generate_mediation_matrix(self.dsm)
        matrices_compliant = Archan._matrices_compliance(self.dsm, med_matrix)
        # check comparison result
        return matrices_compliant

    def economy_of_mechanism(self):
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
        dependency_matrix = self.dsm.dependency_matrix
        categories = self.dsm.categories
        dsm_size = self.dsm.size

        dependency_number = 0
        # evaluate Matrix(dependency_matrix)
        for i in range(0, dsm_size):
            for j in range(0, dsm_size):
                if (categories[i] != self.dsm.framework and
                        categories[j] != self.dsm.framework and
                        dependency_matrix[i][j] > 0):
                    dependency_number += 1
                    # check comparison result
        if dependency_number < dsm_size * self.simplicity_factor:
            economy_of_mechanism = True
        else:
            print("dependency_number: %s" % dependency_number)
            print("rowsdep_matrix: %s" % dsm_size)
            print("expected dependencies: %s" % self.simplicity_factor)
        return economy_of_mechanism

    def least_common_mechanism(self):
        """Check least common mechanism.

        :type dsm: :class:`DesignStructureMatrix`
        :param dsm: matrix to check
        :return: bool
        """

        # leastCommonMechanismMatrix
        least_common_mechanism = False
        # get the list of dependent modules for each module
        dependency_matrix = self.dsm.dependency_matrix
        categories = self.dsm.categories
        dsm_size = self.dsm.size

        dependent_module_number = []
        # evaluate Matrix(dependency_matrix)
        for j in range(0, dsm_size):
            dependent_module_number.append(0)
            for i in range(0, dsm_size):
                if (categories[i] != self.dsm.framework and
                        categories[j] != self.dsm.framework and
                        dependency_matrix[i][j] > 0):
                    dependent_module_number[j] += 1
        # except for the broker if any  and libs, check that threshold is not
        # overlapped
        #  index of brokers
        #  and app_libs are set to 0
        for index, item in enumerate(self.dsm.categories):
            if (item == self.dsm.broker or
                    item == self.dsm.app_lib):
                dependent_module_number[index] = 0
        if max(dependent_module_number) <= old_div(self.dsm.size, self.independence_factor):  # noqa
            least_common_mechanism = True
        else:
            print('max number of dependencies to a module: %s' %
                  max(dependent_module_number))
            print('max number of expected dependencies: %s' %
                  int(old_div(self.dsm.size, self.independence_factor)))

        return least_common_mechanism

    def layered_architecture(self):
        """Check layered architecture.

        :type dsm: :class:`DesignStructureMatrix`
        :param dsm: matrix to check
        :return: bool
        """

        for i in range(0, self.dsm.size - 1):
            for j in range(i + 1, self.dsm.size):
                if (self.dsm.categories[i] != self.dsm.broker and
                            self.dsm.categories[j] != self.dsm.broker):
                    if self.dsm.dependency_matrix[i][j] > 0:
                        return False
        return True

    def open_design(self):
        """Check if all criteria checking methods are implemented.

        :return: bool, True if all methods are implemented, else False
        """

        # check that compliance with secure design principles are performed
        open_design = all(self.checker(flag).__name__ != (lambda: 0).__name__
                          for flag in Archan.FLAGS)
        return open_design

