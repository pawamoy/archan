# -*- coding: utf-8 -*-

"""Main test module."""

from archan.dsm import DesignStructureMatrix as DSM
from archan.plugins.checkers import (
    Checker,
    CompleteMediation,
    EconomyOfMechanism,
    LayeredArchitecture,
    LeastCommonMechanism,
    LeastPrivileges,
    SeparationOfPrivileges,
)


class TestCheckers:
    """
    Main test class.

    It sets up two fake "webapp" and "genida" DSMs to check them.
    """

    @classmethod
    def setup_class(cls):
        """Setup function."""
        web_app_categories = [
            "appmodule",
            "appmodule",
            "appmodule",
            "appmodule",
            "broker",
            "applib",
            "data",
            "data",
            "data",
            "framework",
            "framework",
        ]

        web_app_entities = [
            "store",
            "personal_information",
            "order",
            "payment",
            "available_services",
            "store_lib",
            "store_data",
            "client_data",
            "order_data",
            "framework",
            "login",
        ]

        web_app_dependency_matrix = [
            [1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 0],
            [0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0],
            [0, 0, 1, 0, 1, 0, 0, 0, 1, 1, 0],
            [0, 0, 0, 1, 1, 0, 0, 0, 0, 1, 0],
            [1, 1, 1, 1, 1, 0, 0, 0, 0, 1, 0],  # broker
            [0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 1, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 1, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0],
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 1],
        ]

        cls.web_app_dsm = DSM(web_app_dependency_matrix, web_app_entities, web_app_categories)

        genida_categories = [
            "framework",
            "corelib",
            "corelib",
            "corelib",
            "corelib",
            "corelib",
            "corelib",
            "corelib",
            "corelib",
            "corelib",
            "corelib",
            "corelib",
            "corelib",
            "corelib",
            "corelib",
            "applib",
            "applib",
            "appmodule",
            "applib",
            "applib",
            "applib",
            "appmodule",
            "appmodule",
            "appmodule",
            "appmodule",
            "appmodule",
            "broker",
        ]

        genida_entities = [
            "django",
            "axes",
            "modeltranslation",
            "suit",
            "markdown_deux",
            "cities_light",
            "avatar",
            "djangobower",
            "rosetta",
            "imagekit",
            "smart_selects",
            "captcha",
            "datetimewidget",
            "django_forms_bootstrap",
            "pagedown",
            "dataforms",
            "graph",
            "news",
            "cs_models",
            "zxcvbn_password",
            "dependenpy",
            "complex",
            "questionnaires",
            "members",
            "genida",
            "security",
            "services",
        ]

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
            [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 1, 1, 1, 1, 1],
        ]

        cls.genida_dsm = DSM(genida_dependency_matrix, genida_entities, genida_categories)

    # Webapp tests
    def test_webapp_complete_mediation(self):
        """Test complete mediation for webapp."""
        check = CompleteMediation()
        check.run(self.web_app_dsm)
        result = check.result
        assert result.code == Checker.Code.PASSED, "Complete mediation: %s" % result.messages

    def test_webapp_economy_of_mechanism(self):
        """Test economoy of mechanism for webapp."""
        check = EconomyOfMechanism()
        check.run(self.web_app_dsm)
        result = check.result
        assert result.code == Checker.Code.PASSED, "Economy of mechanism %s" % result.messages

    def test_webapp_least_common_mechanism(self):
        """Test least common mechanism for webapp."""
        check = LeastCommonMechanism()
        check.run(self.web_app_dsm)
        result = check.result
        assert result.code == Checker.Code.PASSED, "Least common mechanism %s" % result.messages

    # def test_webapp_code_clean(self):
    #     """Test code clean for webapp."""
    #     result = CodeClean().run(self.web_app_dsm)
    #     assert result.code == Checker.Code.NOT_IMPLEMENTED,
    #                      'Code clean %s' % result.messages)

    def test_webapp_layered_architecture(self):
        """Test layered architecture for webapp."""
        check = LayeredArchitecture()
        check.run(self.web_app_dsm)
        result = check.result
        assert result.code == Checker.Code.FAILED, "Layered architecture %s" % result.messages

    def test_webapp_least_privileges(self):
        """Test least privileges for webapp."""
        check = LeastPrivileges()
        check.run(self.web_app_dsm)
        result = check.result
        assert result.code == Checker.Code.NOT_IMPLEMENTED, "Least privileges %s" % result.messages

    def test_webapp_separation_of_privileges(self):
        """Test separation of privileges for webapp."""
        check = SeparationOfPrivileges()
        check.run(self.web_app_dsm)
        result = check.result
        assert result.code == Checker.Code.NOT_IMPLEMENTED, "Separation of privileges %s" % result.messages

    # Genida tests
    def test_genida_complete_mediation(self):
        """Test complete mediation for webapp."""
        check = CompleteMediation()
        check.run(self.genida_dsm)
        result = check.result
        assert result.code == Checker.Code.PASSED, "Complete mediation %s" % result.messages

    def test_genida_economy_of_mechanism(self):
        """Test economoy of mechanism for webapp."""
        check = EconomyOfMechanism()
        check.run(self.genida_dsm)
        result = check.result
        assert result.code == Checker.Code.PASSED, "Economy of mechanism %s" % result.messages

    def test_genida_least_common_mechanism(self):
        """Test least common mechanism for webapp."""
        check = LeastCommonMechanism()
        check.run(self.genida_dsm)
        result = check.result
        assert result.code == Checker.Code.PASSED, "Least common mechanism %s" % result.messages

    # def test_genida_code_clean(self):
    #     """Test code clean for webapp."""
    #     result = CodeClean().run(self.genida_dsm)
    #     assert result.code == Checker.Code.NOT_IMPLEMENTED,
    #                      'Code clean %s' % result.messages)

    def test_genida_layered_architecture(self):
        """Test layered architecture for webapp."""
        check = LayeredArchitecture(allow_failure=True)
        check.run(self.genida_dsm)
        result = check.result
        assert result.code == Checker.Code.IGNORED, "Layered architecture %s" % result.messages

    def test_genida_least_privileges(self):
        """Test least privileges for webapp."""
        check = LeastPrivileges(allow_failure=True)
        check.run(self.genida_dsm)
        result = check.result
        assert result.code == Checker.Code.NOT_IMPLEMENTED, "Least privileges %s" % result.messages

    def test_genida_separation_of_privileges(self):
        """Test separation of privileges for webapp."""
        check = SeparationOfPrivileges()
        check.run(self.genida_dsm)
        result = check.result
        assert result.code == Checker.Code.NOT_IMPLEMENTED, "Separation of privileges %s" % result.messages
