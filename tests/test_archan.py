# -*- coding: utf-8 -*-

"""Main test module."""

import unittest

from archan.checkers import (
    Checker, CodeClean, CompleteMediation, EconomyOfMechanism,
    LayeredArchitecture, LeastCommonMechanism, LeastPrivileges, OpenDesign,
    SeparationOfPrivileges)
from archan.dsm import DesignStructureMatrix as DSM


class TestArchan(unittest.TestCase):
    """
    Main test class.

    It sets up two fake "webapp" and "genida" DSMs to check them.
    """

    def setUp(self):
        """Setup function."""
        web_app_categories = ['appmodule', 'appmodule', 'appmodule',
                              'appmodule', 'broker',
                              'applib', 'data', 'data',
                              'data', 'framework', 'framework']
        web_app_entities = ['store', 'personal_information', 'order',
                            'payment', 'available_services',
                            'store_lib', 'store_data', 'client_data',
                            'order_data', 'framework', 'login']
        web_app_dependency_matrix = [[1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0],
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
        self.web_app_dsm = DSM(
            web_app_dependency_matrix, web_app_entities, web_app_categories)
        genida_categories = ['framework',
                             'corelib', 'corelib', 'corelib',
                             'corelib', 'corelib', 'corelib',
                             'corelib', 'corelib', 'corelib',
                             'corelib', 'corelib', 'corelib',
                             'corelib', 'corelib', 'applib',
                             'applib', 'appmodule', 'applib',
                             'applib', 'applib', 'appmodule',
                             'appmodule', 'appmodule', 'appmodule',
                             'appmodule', 'broker']

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
        genida_dependency_matrix = [
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
        self.genida_dsm = DSM(
            genida_dependency_matrix, genida_entities, genida_categories)

    # Webapp tests
    def test_webapp_complete_mediation(self):
        """Test complete mediation for webapp."""
        result = CompleteMediation().run(self.web_app_dsm)
        self.assertEqual(result[0], Checker.PASSED,
                         'Complete mediation: %s' % result[1])

    def test_webapp_economy_of_mechanism(self):
        """Test economoy of mechanism for webapp."""
        result = EconomyOfMechanism().run(self.web_app_dsm)
        self.assertEqual(result[0], Checker.PASSED,
                         'Economy of mechanism %s' % result[1])

    def test_webapp_least_common_mechanism(self):
        """Test least common mechanism for webapp."""
        result = LeastCommonMechanism().run(self.web_app_dsm)
        self.assertEqual(result[0], Checker.PASSED,
                         'Least common mechanism %s' % result[1])

    def test_webapp_code_clean(self):
        """Test code clean for webapp."""
        result = CodeClean().run(self.web_app_dsm)
        self.assertEqual(result[0], Checker.NOT_IMPLEMENTED,
                         'Code clean %s' % result[1])

    def test_webapp_layered_architecture(self):
        """Test layered architecture for webapp."""
        result = LayeredArchitecture().run(self.web_app_dsm)
        self.assertEqual(result[0], Checker.FAILED,
                         'Layered architecture %s' % result[1])

    def test_webapp_least_privileges(self):
        """Test least privileges for webapp."""
        result = LeastPrivileges().run(self.web_app_dsm)
        self.assertEqual(result[0], Checker.NOT_IMPLEMENTED,
                         'Least privileges %s' % result[1])

    def test_webapp_open_design(self):
        """Test open design for webapp."""
        result = OpenDesign(ok=False, ignore=True).run(self.web_app_dsm)
        self.assertEqual(result[0], Checker.IGNORED,
                         'Open design %s' % result[1])

    def test_webapp_separation_of_privileges(self):
        """Test separation of privileges for webapp."""
        result = SeparationOfPrivileges().run(self.web_app_dsm)
        self.assertEqual(result[0], Checker.NOT_IMPLEMENTED,
                         'Separation of privileges %s' % result[1])

    # Genida tests
    def test_genida_complete_mediation(self):
        """Test complete mediation for webapp."""
        result = CompleteMediation().run(self.genida_dsm)
        self.assertEqual(result[0], Checker.PASSED,
                         'Complete mediation %s' % result[1])

    def test_genida_economy_of_mechanism(self):
        """Test economoy of mechanism for webapp."""
        result = EconomyOfMechanism().run(self.genida_dsm)
        self.assertEqual(result[0], Checker.PASSED,
                         'Economy of mechanism %s' % result[1])

    def test_genida_least_common_mechanism(self):
        """Test least common mechanism for webapp."""
        result = LeastCommonMechanism().run(self.genida_dsm)
        self.assertEqual(result[0], Checker.PASSED,
                         'Least common mechanism %s' % result[1])

    def test_genida_code_clean(self):
        """Test code clean for webapp."""
        result = CodeClean().run(self.genida_dsm)
        self.assertEqual(result[0], Checker.NOT_IMPLEMENTED,
                         'Code clean %s' % result[1])

    def test_genida_layered_architecture(self):
        """Test layered architecture for webapp."""
        result = LayeredArchitecture(ignore=True).run(self.genida_dsm)
        self.assertEqual(result[0], Checker.IGNORED,
                         'Layered architecture %s' % result[1])

    def test_genida_least_privileges(self):
        """Test least privileges for webapp."""
        result = LeastPrivileges(ignore=True).run(self.genida_dsm)
        self.assertEqual(result[0], Checker.NOT_IMPLEMENTED,
                         'Least privileges %s' % result[1])

    def test_genida_open_design(self):
        """Test open design for webapp."""
        result = OpenDesign(ok=True).run(self.genida_dsm)
        self.assertEqual(result[0], Checker.PASSED,
                         'Open design %s' % result[1])

    def test_genida_separation_of_privileges(self):
        """Test separation of privileges for webapp."""
        result = SeparationOfPrivileges().run(self.genida_dsm)
        self.assertEqual(result[0], Checker.NOT_IMPLEMENTED,
                         'Separation of privileges %s' % result[1])


if __name__ == '__main__':
    unittest.main()
