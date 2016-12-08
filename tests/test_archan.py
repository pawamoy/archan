# -*- coding: utf-8 -*-

# Copyright (c) 2015 Pierre Parrend
#
# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at http://mozilla.org/MPL/2.0/.

"""
Created on 8 janv. 2015

<<<<<<< HEAD
@author: Pierre.Parrend
"""

from __future__ import unicode_literals

import unittest

from archan.checker import Archan
from archan.criterion import (
    CODE_CLEAN, COMPLETE_MEDIATION, ECONOMY_OF_MECHANISM, LAYERED_ARCHITECTURE,
    LEAST_COMMON_MECHANISM, LEAST_PRIVILEGES, OPEN_DESIGN,
    SEPARATION_OF_PRIVILEGES, Criterion)
from archan.dsm import DesignStructureMatrix


class TestArchan(unittest.TestCase):
    def setUp(self):
        web_app_categories = ['app_module', 'app_module', 'app_module',
                              'app_module', 'broker',
                              'app_lib', 'data', 'data',
                              'data', 'framework', 'framework']
        web_app_entities = ['store', 'personal_information', 'order',
                            'payment', 'available_services',
                            'store_lib', 'store_data', 'client_data',
                            'order_data', 'framework', 'login']
        web_app_dsm = [[1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0],
                       [0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0],
                       [0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0],
                       [0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0],
                       [1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0],  # broker
                       [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
                       [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
                       [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
                       [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1]]
        self.web_app_dependency_matrix = DesignStructureMatrix(
            web_app_categories, web_app_entities, web_app_dsm)
        genida_categories = ['framework',
                             'core_lib', 'core_lib', 'core_lib',
                             'core_lib', 'core_lib', 'core_lib',
                             'core_lib', 'core_lib', 'core_lib',
                             'core_lib', 'core_lib', 'core_lib',
                             'core_lib', 'core_lib', 'app_lib',
                             'app_lib', 'app_module', 'app_lib',
                             'app_lib', 'app_lib', 'app_module',
                             'app_module', 'app_module', 'app_module',
                             'app_module', 'broker']

        genida_entities = ['django',
                           'axes', 'modeltranslation', 'suit',
                           'markdown_deux', 'cities_light', 'avatar',
                           'djangobower', 'rosetta', 'imagekit',
                           'smart_selects', 'captcha', 'datetimewidget',
                           'django_forms_bootstrap', 'pagedown', 'dataforms',
                           'graph', 'news', 'cs_models',
                           'zxcvbn_password', 'dependenpy', 'complex',
                           'questionnaires', 'members', 'genida',
                           'security', 'services']

        # NOQA
        genida_dsm = [
            [4438, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [30, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [50, 0, 41, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [41, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [3, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [43, 0, 0, 0, 0, 45, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [32, 0, 0, 0, 0, 0, 31, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [12, 0, 0, 0, 0, 0, 0, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [36, 0, 0, 0, 0, 0, 0, 0, 19, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [33, 0, 0, 0, 0, 0, 0, 0, 0, 66, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [31, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 17, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [75, 0, 2, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 97, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0],
            [12, 0, 2, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 1, 0, 0, 13, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
            [13, 0, 0, 0, 0, 3, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 7, 0, 0, 0, 0, 1],
            [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [22, 0, 0, 0, 0, 2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [26, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0, 0, 0, 0, 0, 1],
            [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1]]
        self.genida_dependency_matrix = DesignStructureMatrix(
            genida_categories, genida_entities, genida_dsm)

        archan = Archan()
        self.result_webapp = archan.check(self.web_app_dependency_matrix)
        self.result_genida = archan.check(
            self.genida_dependency_matrix, criteria=[
                COMPLETE_MEDIATION, ECONOMY_OF_MECHANISM,
                LEAST_COMMON_MECHANISM])

        self.message = {
            Criterion.PASSED: 'PASSED',
            Criterion.FAILED: 'FAILED',
            Criterion.NOT_IMPLEMENTED: 'NOT IMPLEMENTED',
            Criterion.IGNORED: 'IGNORED'
        }

    # Webapp tests
    def test_webapp_complete_mediation(self):
        result = self.result_webapp[COMPLETE_MEDIATION.codename]
        self.assertEqual(result[0], Criterion.PASSED,
                         'Complete mediation %s: %s' % (
                             self.message[result[0]], result[1]))

    def test_webapp_economy_of_mechanism(self):
        result = self.result_webapp[ECONOMY_OF_MECHANISM.codename]
        self.assertEqual(result[0], Criterion.PASSED,
                         'Economy of mechanism %s: %s' % (
                             self.message[result[0]], result[1]))

    def test_webapp_least_common_mechanism(self):
        result = self.result_webapp[LEAST_COMMON_MECHANISM.codename]
        self.assertEqual(result[0], Criterion.PASSED,
                         'Least common mechanism %s: %s' % (
                             self.message[result[0]], result[1]))

    def test_webapp_code_clean(self):
        result = self.result_webapp[CODE_CLEAN.codename]
        self.assertEqual(result[0], Criterion.NOT_IMPLEMENTED,
                         'Code clean %s: %s' % (
                             self.message[result[0]], result[1]))

    def test_webapp_layered_architecture(self):
        result = self.result_webapp[LAYERED_ARCHITECTURE.codename]
        self.assertEqual(result[0], Criterion.FAILED,
                         'Layered architecture %s: %s' % (
                             self.message[result[0]], result[1]))

    def test_webapp_least_privileges(self):
        result = self.result_webapp[LEAST_PRIVILEGES.codename]
        self.assertEqual(result[0], Criterion.NOT_IMPLEMENTED,
                         'Least privileges %s: %s' % (
                             self.message[result[0]],
                             result[1]))

    def test_webapp_open_design(self):
        result = self.result_webapp[OPEN_DESIGN.codename]
        self.assertEqual(result[0], Criterion.NOT_IMPLEMENTED,
                         'Open design %s: %s' % (
                             self.message[result[0]], result[1]))

    def test_webapp_separation_of_privileges(self):
        result = self.result_webapp[SEPARATION_OF_PRIVILEGES.codename]
        self.assertEqual(result[0], Criterion.NOT_IMPLEMENTED,
                         'Separation of privileges %s: %s' % (
                             self.message[result[0]], result[1]))

    # Genida tests
    def test_genida_complete_mediation(self):
        result = self.result_genida[COMPLETE_MEDIATION.codename]
        self.assertEqual(result[0], Criterion.PASSED,
                         'Complete mediation %s: %s' % (
                             self.message[result[0]], result[1]))

    def test_genida_economy_of_mechanism(self):
        result = self.result_genida[ECONOMY_OF_MECHANISM.codename]
        self.assertEqual(result[0], Criterion.PASSED,
                         'Economy of mechanism %s: %s' % (
                             self.message[result[0]], result[1]))

    def test_genida_least_common_mechanism(self):
        result = self.result_genida[LEAST_COMMON_MECHANISM.codename]
        self.assertEqual(result[0], Criterion.PASSED,
                         'Least common mechanism %s: %s' % (
                             self.message[result[0]], result[1]))

    def test_genida_code_clean(self):
        result = self.result_genida[CODE_CLEAN.codename]
        self.assertEqual(result[0], Criterion.IGNORED,
                         'Code clean %s: %s' % (
                             self.message[result[0]], result[1]))

    def test_genida_layered_architecture(self):
        result = self.result_genida[LAYERED_ARCHITECTURE.codename]
        self.assertEqual(result[0], Criterion.IGNORED,
                         'Layered architecture %s: %s' % (
                             self.message[result[0]], result[1]))

    def test_genida_least_privileges(self):
        result = self.result_genida[LEAST_PRIVILEGES.codename]
        self.assertEqual(result[0], Criterion.IGNORED,
                         'Least privileges %s: %s' % (
                             self.message[result[0]], result[1]))

    def test_genida_open_design(self):
        result = self.result_genida[OPEN_DESIGN.codename]
        self.assertEqual(result[0], Criterion.IGNORED,
                         'Open design %s: %s' % (
                             self.message[result[0]], result[1]))

    def test_genida_separation_of_privileges(self):
        result = self.result_genida[SEPARATION_OF_PRIVILEGES.codename]
        self.assertEqual(result[0], Criterion.IGNORED,
                         'Separation of privileges %s: %s' % (
                             self.message[result[0]], result[1]))

    # General tests
    def test_ignored(self):
        archan = Archan()
        result = archan.check(self.web_app_dependency_matrix,
                              criteria=[CODE_CLEAN])
        self.assertEqual(result[OPEN_DESIGN.codename][0],
                         Criterion.IGNORED,
                         'Ignored criteria do not return IGNORED.')

    def test_not_implemented(self):
        archan = Archan(criteria=[CODE_CLEAN])
        result = archan.check(self.web_app_dependency_matrix)
        self.assertEqual(result[CODE_CLEAN.codename][0],
                         Criterion.NOT_IMPLEMENTED,
                         'Not implemented criteria '
                         'do not return NOT IMPLEMENTED.')
        self.assertNotIn(OPEN_DESIGN.codename, result,
                         'Open design should NOT be in the criteria list.')


if __name__ == '__main__':
    unittest.main()

