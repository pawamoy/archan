# -*- coding: utf-8 -*-

"""
DSM module.

Contains the DesignStructureMatrix, DomainMappingMatrix and
MultipleDomainMatrix classes.
"""

from .errors import DesignStructureMatrixError, DomainMappingMatrixError, MatrixError, MultipleDomainMatrixError


def validate_rows_length(data, length, message=None, exception=MatrixError):
    """Validate that all rows have the same length."""
    if message is None:
        message = "All rows must have the same length (same number of columns)"
    for row in data:
        if len(row) != length:
            raise exception(message)


def validate_square(data, message=None, exception=MatrixError):
    """Validate that the matrix has equal number of rows and columns."""
    rows, columns = len(data), len(data[0]) if data else 0
    if message is None:
        message = "Number of rows: %s != number of columns: %s in matrix" % (rows, columns)
    if rows != columns:
        raise exception(message)


def validate_categories_equal_entities(categories, entities, message=None, exception=MatrixError):
    """Validate that the matrix has equal number of entities and categories."""
    nb_categories = len(categories)
    nb_entities = len(entities)
    if message is None:
        message = "Number of categories: %s != number of entities: %s" % (nb_categories, nb_entities)
    if categories and nb_categories != nb_entities:
        raise exception(message)


class BaseMatrix(object):
    """Base class for matrix classes."""

    # TODO: also consider these attributes:
    # output on rows, output on columns,
    # static, time_based,
    # binary, numeric, probability
    error = MatrixError
    square = False

    def __init__(self, data, entities=None, categories=None):
        """
        Initialization method.

        Args:
            data (list of list of int/float): 2-dim array.
            entities (list): list of entities.
            categories (list): list of the categories (one per entity).
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
    def rows(self):
        """Return number of rows in data."""
        return len(self.data)

    @property
    def columns(self):
        """Return number of columns in data."""
        return len(self.data[0]) if self.data else 0

    @property
    def size(self):
        """Return number of rows and columns in data."""
        return self.rows, self.columns

    def validate(self):
        """Validate data (rows length, categories=entities, square)."""
        validate_rows_length(self.data, self.columns, exception=self.error)
        validate_categories_equal_entities(self.categories, self.entities, exception=self.error)
        if self.square:
            validate_square(self.data, exception=self.error)

    def default_entities(self):
        """Default entities used when there are none."""
        return [str(i) for i in range(self.rows)]


class DesignStructureMatrix(BaseMatrix):
    """Design Structure Matrix class."""

    error = DesignStructureMatrixError
    square = True

    def validate(self):
        """Base validation + entities = rows."""
        super().validate()
        nb_entities = len(self.entities)
        if nb_entities != self.rows:
            raise self.error("Number of entities: %s != number of rows: %s" % (nb_entities, self.rows))

    def transitive_closure(self):
        """Compute the transitive closure of the matrix."""
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

    def validate(self):
        """Base validation + entities = rows + columns."""
        super().validate()
        nb_entities = len(self.entities)
        if nb_entities != self.rows + self.columns:
            raise self.error(
                "Number of entities: %s != number of rows + "
                "number of columns: %s+%s=%s" % (nb_entities, self.rows, self.columns, self.rows + self.columns)
            )

    def default_entities(self):
        """Return range from 0 to rows + columns."""
        return [str(i) for i in range(self.rows + self.columns)]


class MultipleDomainMatrix(BaseMatrix):
    """Multiple Domain Matrix class."""

    error = MultipleDomainMatrixError
    square = True

    def validate(self):
        """Base validation + each cell is instance of DSM or MDM."""
        super().validate()
        message_dsm = "Matrix at [%s:%s] is not an instance of " "DesignStructureMatrix or MultipleDomainMatrix."
        message_ddm = "Matrix at [%s:%s] is not an instance of " "DomainMappingMatrix or MultipleDomainMatrix."
        messages = []
        for i, row in enumerate(self.data):
            for j, cell in enumerate(row):
                if i == j:
                    if not isinstance(cell, (DesignStructureMatrix, MultipleDomainMatrix)):
                        messages.append(message_dsm % (i, j))
                elif not isinstance(cell, (DomainMappingMatrix, MultipleDomainMatrix)):
                    messages.append(message_ddm % (i, j))
        if messages:
            raise self.error("\n".join(messages))
