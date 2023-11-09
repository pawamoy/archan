"""DSM module.

Contains the DesignStructureMatrix, DomainMappingMatrix and
MultipleDomainMatrix classes.
"""

from __future__ import annotations

from archan.errors import DesignStructureMatrixError, DomainMappingMatrixError, MatrixError, MultipleDomainMatrixError


def validate_rows_length(
    data: list[list],
    length: int,
    message: str | None = None,
    exception: type = MatrixError,
) -> None:
    """Validate that all rows have the same length.

    Parameters:
        data: The data to validate.
        length: The length to enforce.
        message: The exception message.
        exception: The exception type.

    Raises:
        MatrixError: When the validation failed.
    """
    if message is None:
        message = "All rows must have the same length (same number of columns)"
    for row in data:
        if len(row) != length:
            raise exception(message)


def validate_square(data: list[list], message: str | None = None, exception: type = MatrixError) -> None:
    """Validate that the matrix has equal number of rows and columns.

    Parameters:
        data: The data to validate.
        message: The exception message.
        exception: The exception type.

    Raises:
        MatrixError: When the validation failed.
    """
    rows, columns = len(data), len(data[0]) if data else 0
    if message is None:
        message = f"Number of rows: {rows} != number of columns: {columns} in matrix"
    if rows != columns:
        raise exception(message)


def validate_categories_equal_entities(
    categories: list,
    entities: list,
    message: str | None = None,
    exception: type = MatrixError,
) -> None:
    """Validate that the matrix has equal number of entities and categories.

    Parameters:
        categories: The categories to validate.
        entities: The entities to validate.
        message: The exception message.
        exception: The exception type.

    Raises:
        MatrixError: When the validation failed.
    """
    nb_categories = len(categories)
    nb_entities = len(entities)
    if message is None:
        message = f"Number of categories: {nb_categories} != number of entities: {nb_entities}"
    if categories and nb_categories != nb_entities:
        raise exception(message)


class BaseMatrix:
    """Base class for matrix classes."""

    # TODO: also consider these attributes:
    # output on rows, output on columns,
    # static, time_based,
    # binary, numeric, probability
    error = MatrixError
    square = False

    def __init__(self, data: list[list[int | float]], entities: list | None = None, categories: list | None = None):
        """Initialization method.

        Parameters:
            data: 2-dim array.
            entities: List of entities.
            categories: List of the categories (one per entity).
        """
        self.data = data
        if entities is None:
            entities = self.default_entities()
        self.entities = entities
        if categories is None:
            categories = []
        self.categories = categories

        self.validate()

    @property
    def rows(self) -> int:
        """Return number of rows in data.

        Returns:
            The number of rows.
        """
        return len(self.data)

    @property
    def columns(self) -> int:
        """Return number of columns in data.

        Returns:
            The number of columns.
        """
        return len(self.data[0]) if self.data else 0

    @property
    def size(self) -> tuple[int, int]:
        """Return number of rows and columns in data.

        Returns:
            The dimensions of the data.
        """
        return self.rows, self.columns

    def validate(self) -> None:
        """Validate data (rows length, categories=entities, square)."""
        validate_rows_length(self.data, self.columns, exception=self.error)
        validate_categories_equal_entities(self.categories, self.entities, exception=self.error)
        if self.square:
            validate_square(self.data, exception=self.error)

    def default_entities(self) -> list[str]:
        """Default entities used when there are none.

        Returns:
            The default entities.
        """
        return [str(_) for _ in range(self.rows)]


class DesignStructureMatrix(BaseMatrix):
    """Design Structure Matrix class."""

    error = DesignStructureMatrixError
    square = True

    def validate(self) -> None:
        """Base validation + entities = rows.

        Raises:
            DesignStructureMatrixError: When number of entities is different than number of rows.
        """
        super().validate()
        nb_entities = len(self.entities)
        if nb_entities != self.rows:
            raise self.error(f"Number of entities: {nb_entities} != number of rows: {self.rows}")

    def transitive_closure(self) -> list[list[int]]:
        """Compute the transitive closure of the matrix.

        Returns:
            The transitive closure of the matrix.
        """
        data = [[1 if j else 0 for j in i] for i in self.data]
        for k in range(self.rows):
            for i in range(self.rows):
                for j in range(self.rows):
                    if data[i][k] and data[k][j]:
                        data[i][j] = 1
        return data


class DomainMappingMatrix(BaseMatrix):
    """Domain Mapping Matrix class."""

    error = DomainMappingMatrixError

    def validate(self) -> None:
        """Base validation + entities = rows + columns.

        Raises:
            DomainMappingMatrixError: When number of entities is different than rows plus columns.
        """
        super().validate()
        nb_entities = len(self.entities)
        if nb_entities != self.rows + self.columns:
            raise self.error(
                f"Number of entities: {nb_entities} != number of rows + "
                f"number of columns: {self.rows}+{self.columns}={self.rows + self.columns}",
            )

    def default_entities(self) -> list[str]:
        """Return range from 0 to rows + columns.

        Returns:
            Range from 0 to rows + columns.
        """
        return [str(_) for _ in range(self.rows + self.columns)]


class MultipleDomainMatrix(BaseMatrix):
    """Multiple Domain Matrix class."""

    error = MultipleDomainMatrixError
    square = True

    def validate(self) -> None:
        """Base validation + each cell is instance of DSM or MDM.

        Raises:
            MultipleDomainMatrixError: When diagonal cells are not DSM nor MDM, or when other cells are not DMM nor MDM.
        """
        super().validate()
        message_dsm = "Matrix at [%s:%s] is not an instance of DesignStructureMatrix or MultipleDomainMatrix."
        message_ddm = "Matrix at [%s:%s] is not an instance of DomainMappingMatrix or MultipleDomainMatrix."
        messages = []
        for line, row in enumerate(self.data):
            for column, cell in enumerate(row):
                if line == column:
                    if not isinstance(cell, (DesignStructureMatrix, MultipleDomainMatrix)):
                        messages.append(message_dsm % (line, column))
                elif not isinstance(cell, (DomainMappingMatrix, MultipleDomainMatrix)):
                    messages.append(message_ddm % (line, column))
        if messages:
            raise self.error("\n".join(messages))
