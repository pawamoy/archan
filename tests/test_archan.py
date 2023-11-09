"""Main test module."""

from typing import TYPE_CHECKING

from archan.dsm import DesignStructureMatrix as DSM  # noqa: N817
from archan.plugins.checkers import (
    Checker,
    CompleteMediation,
    EconomyOfMechanism,
    LayeredArchitecture,
    LeastCommonMechanism,
    LeastPrivileges,
    SeparationOfPrivileges,
)

if TYPE_CHECKING:
    from archan.analysis import Result


class TestCheckers:
    """Main test class.

    It sets up two fake "webapp" and "genida" DSMs to check them.
    """

    web_app_dsm: DSM
    genida_dsm: DSM

    @classmethod
    def setup_class(cls) -> None:
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

        cls.web_app_dsm = DSM(web_app_dependency_matrix, web_app_entities, web_app_categories)  # type: ignore[arg-type]

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

        cls.genida_dsm = DSM(genida_dependency_matrix, genida_entities, genida_categories)  # type: ignore[arg-type]

    # Webapp tests
    def test_webapp_complete_mediation(self) -> None:
        """Test complete mediation for webapp."""
        check = CompleteMediation()
        check.run(self.web_app_dsm)
        result: Result = check.result  # type: ignore[assignment]
        assert result.code == Checker.Code.PASSED, f"Complete mediation: {result.messages}"

    def test_webapp_economy_of_mechanism(self) -> None:
        """Test economoy of mechanism for webapp."""
        check = EconomyOfMechanism()
        check.run(self.web_app_dsm)
        result: Result = check.result  # type: ignore[assignment]
        assert result.code == Checker.Code.PASSED, f"Economy of mechanism: {result.messages}"

    def test_webapp_least_common_mechanism(self) -> None:
        """Test least common mechanism for webapp."""
        check = LeastCommonMechanism()
        check.run(self.web_app_dsm)
        result: Result = check.result  # type: ignore[assignment]
        assert result.code == Checker.Code.PASSED, f"Least common mechanism: {result.messages}"

    # def test_webapp_code_clean(self) -> None:
    #     """Test code clean for webapp."""
    #     result: Result = CodeClean().run(self.web_app_dsm)
    #     assert result.code == Checker.Code.NOT_IMPLEMENTED, f"Code clean: {result.messages}"

    def test_webapp_layered_architecture(self) -> None:
        """Test layered architecture for webapp."""
        check = LayeredArchitecture()
        check.run(self.web_app_dsm)
        result: Result = check.result  # type: ignore[assignment]
        assert result.code == Checker.Code.FAILED, f"Layered architecture: {result.messages}"

    def test_webapp_least_privileges(self) -> None:
        """Test least privileges for webapp."""
        check = LeastPrivileges()
        check.run(self.web_app_dsm)
        result: Result = check.result  # type: ignore[assignment]
        assert result.code == Checker.Code.NOT_IMPLEMENTED, f"Least privileges: {result.messages}"

    def test_webapp_separation_of_privileges(self) -> None:
        """Test separation of privileges for webapp."""
        check = SeparationOfPrivileges()
        check.run(self.web_app_dsm)
        result: Result = check.result  # type: ignore[assignment]
        assert result.code == Checker.Code.NOT_IMPLEMENTED, f"Separation of privileges: {result.messages}"

    # Genida tests
    def test_genida_complete_mediation(self) -> None:
        """Test complete mediation for webapp."""
        check = CompleteMediation()
        check.run(self.genida_dsm)
        result: Result = check.result  # type: ignore[assignment]
        assert result.code == Checker.Code.PASSED, f"Complete mediation: {result.messages}"

    def test_genida_economy_of_mechanism(self) -> None:
        """Test economoy of mechanism for webapp."""
        check = EconomyOfMechanism()
        check.run(self.genida_dsm)
        result: Result = check.result  # type: ignore[assignment]
        assert result.code == Checker.Code.PASSED, f"Economy of mechanism: {result.messages}"

    def test_genida_least_common_mechanism(self) -> None:
        """Test least common mechanism for webapp."""
        check = LeastCommonMechanism()
        check.run(self.genida_dsm)
        result: Result = check.result  # type: ignore[assignment]
        assert result.code == Checker.Code.PASSED, f"Least common mechanism: {result.messages}"

    # def test_genida_code_clean(self) -> None:
    #     """Test code clean for webapp."""
    #     result: Result = CodeClean().run(self.genida_dsm)
    #     assert result.code == Checker.Code.NOT_IMPLEMENTED, f"Code clean: {result.messages}"

    def test_genida_layered_architecture(self) -> None:
        """Test layered architecture for webapp."""
        check = LayeredArchitecture(allow_failure=True)
        check.run(self.genida_dsm)
        result: Result = check.result  # type: ignore[assignment]
        assert result.code == Checker.Code.IGNORED, f"Layered architecture: {result.messages}"

    def test_genida_least_privileges(self) -> None:
        """Test least privileges for webapp."""
        check = LeastPrivileges(allow_failure=True)
        check.run(self.genida_dsm)
        result: Result = check.result  # type: ignore[assignment]
        assert result.code == Checker.Code.NOT_IMPLEMENTED, f"Least privileges: {result.messages}"

    def test_genida_separation_of_privileges(self) -> None:
        """Test separation of privileges for webapp."""
        check = SeparationOfPrivileges()
        check.run(self.genida_dsm)
        result: Result = check.result  # type: ignore[assignment]
        assert result.code == Checker.Code.NOT_IMPLEMENTED, f"Separation of privileges: {result.messages}"
