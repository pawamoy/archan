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

from __future__ import unicode_literals

import unittest

from archan.checker import Archan
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

        genida_dsm = [
            [4438, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0],
            [30, 14, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0],
            [50, 0, 41, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0],
            [41, 0, 0, 5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0],
            [3, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0],
            [43, 0, 0, 0, 0, 45, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0],
            [32, 0, 0, 0, 0, 0, 31, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0],
            [12, 0, 0, 0, 0, 0, 0, 16, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0],
            [36, 0, 0, 0, 0, 0, 0, 0, 19, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0],
            [33, 0, 0, 0, 0, 0, 0, 0, 0, 66, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0],
            [12, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0],
            [31, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 17, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0],
            [10, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0],
            [3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0],
            [11, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0],
            [75, 0, 2, 1, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 97, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0, 0],
            [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 0, 0, 0, 2, 0,
             0, 0, 0, 0, 0],
            [12, 0, 2, 0, 0, 0, 0, 0, 0, 5, 0, 0, 0, 0, 1, 0, 0, 13, 0, 0, 0,
             0, 0, 0, 0, 0, 1],
            [5, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0],
            [7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0,
             0, 0, 0, 0, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 0],
            [13, 0, 0, 0, 0, 3, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 7,
             0, 0, 0, 0, 1],
            [8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 7, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 1],
            [22, 0, 0, 0, 0, 2, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 1],
            [26, 1, 2, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 2, 0, 0,
             0, 0, 0, 0, 1],
            [4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
             0, 0, 0, 0, 1],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1,
             1, 1, 1, 1, 1]]
        self.genida_dm = DesignStructureMatrix(
            genida_categories, genida_entities, genida_dsm)
    # 0 for items which MUST NOT be present
    # 1 for items which MUST be present
    completeMediationMatrixOnlineStore = [
        [-1, 0, 0, 0, 1, -1, -1, -1, -1, -1, -1],  # app modules
        [0, -1, 0, 0, 1, -1, -1, -1, -1, -1, -1],
        [0, 0, -1, 0, 1, -1, -1, -1, -1, -1, -1],
        [0, 0, 0, -1, 1, -1, -1, -1, -1, -1, -1],
        [1, 1, 1, 1, -1, 0, 0, 0, 0, -1, -1],  # broker
        [0, 0, 0, 0, 0, -1, 0, 0, 0, -1, -1],  # libs
        [0, 0, 0, 0, 0, 0, -1, 0, 0, -1, -1],  # data
        [0, 0, 0, 0, 0, 0, 0, -1, 0, -1, -1],
        [0, 0, 0, 0, 0, 0, 0, 0, -1, -1, -1],
        [0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1],  # framework
        [0, 0, 0, 0, 0, 0, 0, 0, 0, -1, -1]]  # framework

    def test_mediation_matrix_generation(self):
        archan = Archan()
        # referenceDSM = self.web_app_dependency_matrix.getDependencyMatrix()
        reference_mediation_matrix = self.completeMediationMatrixOnlineStore
        generate_mediation_matrix = archan._generate_mediation_matrix(
            self.web_app_dependency_matrix)

        generation_complete = True
        ri, rj = [], []
        for i in range(1, self.web_app_dependency_matrix.size):
            for j in range(1, self.web_app_dependency_matrix.size):
                if reference_mediation_matrix[i][j] != \
                        generate_mediation_matrix[i][j]:
                    generation_complete = False
                    ri += i
                    rj += j

        self.assertTrue(generation_complete,
                        "Error in generation of the compliance matrix "
                        "at lines %s, columns %s" % (ri, rj))

    def test_complete_mediation(self):
        archan = Archan()
        compliant = archan.check_complete_mediation(
            self.web_app_dependency_matrix)
        self.assertTrue(compliant,
                        "Complete Mediation is NOT enforced")

    def test_economy_of_mechanism(self):
        archan = Archan()
        economy_of_mechanism = archan.check_economy_of_mechanism(
            self.web_app_dependency_matrix)
        self.assertTrue(economy_of_mechanism,
                        "Economy of Mechanism is NOT enforced")

    def test_least_common_mechanism(self):
        archan = Archan()
        least_common_mechanism = archan.check_least_common_mechanism(
            self.web_app_dependency_matrix)
        self.assertTrue(least_common_mechanism,
                        "Least common Mechanism is NOT enforced")

    def test_open_design(self):
        archan = Archan()
        open_design = archan.check_open_design()
        self.assertTrue(open_design,
                        "Open Design is NOT enforced")


if __name__ == '__main__':
    unittest.main()
