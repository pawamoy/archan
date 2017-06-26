# -*- coding: utf-8 -*-

"""
DSM module.

Contains the DesignStructureMatrix, DomainMappingMatrix and
MultipleDomainMatrix classes.
"""

from .errors import DSMError


def validate_rows_length(data, length, message=None):
    if message is None:
        message = 'All rows must have the same length (same number of columns)'
    for row in data:
        if len(row) != length:
            raise DSMError(message)


def validate_square(data, message=None):
    rows, columns = len(data), len(data[0])
    if message is None:
        message = 'Number of rows: %s != number of columns: %s in matrix' % (
            rows, columns)
    if rows != columns:
        raise DSMError(message)


def validate_categories_equal_entities(categories, entities, message=None):
    nb_categories = len(categories)
    nb_entities = len(entities)
    if message is None:
        message = 'Number of categories: %s != number of entities: %s' % (
            nb_categories, nb_entities)
    if categories and nb_categories != nb_entities:
        raise DSMError(message)


class BaseMatrix(object):
    # TODO: also consider these attributes:
    # output on rows, output on columns,
    # static, time_based,
    # binary, numeric, probability
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
        return len(self.data)

    @property
    def columns(self):
        return len(self.data[0])

    @property
    def size(self):
        return self.rows, self.columns

    def validate(self):
        validate_rows_length(self.data, self.columns)
        validate_categories_equal_entities(self.categories, self.entities)
        if self.square:
            validate_square(self.data)

    def default_entities(self):
        return [str(i) for i in range(self.rows)]


class DesignStructureMatrix(BaseMatrix):
    """Design Structure Matrix class."""

    square = True

    def validate(self):
        super().validate()
        nb_entities = len(self.entities)
        if nb_entities != self.rows:
            raise DSMError(
                'Number of entities: %s != number of rows: %s' % (
                    nb_entities, self.rows))

    def transitive_closure(self):
        data = [[1 if j else 0 for j in i] for i in self.data]
        for k in range(self.rows):
            for i in range(self.rows):
                for j in range(self.rows):
                    if data[i][k] and data[k][j]:
                        data[i][j] = 1
        return data


class DomainMappingMatrix(BaseMatrix):
    """Domain Mapping Matrix class."""

    def validate(self):
        super().validate()
        nb_entities = len(self.entities)
        if nb_entities != self.rows + self.columns:
            raise DSMError(
                'Number of entities: %s != number of rows + '
                'number of columns: %s+%s=%s' % (
                    nb_entities, self.rows, self.columns,
                    self.rows + self.columns))

    def default_entities(self):
        return [str(i) for i in range(self.rows + self.columns)]


class MultipleDomainMatrix(BaseMatrix):
    """Multiple Domain Matrix class."""

    square = True

    def validate(self):
        super().validate()
        message_dsm = 'Matrix at [%s:%s] is not an instance of '\
                      'DesignStructureMatrix or MultipleDomainMatrix.'
        message_ddm = 'Matrix at [%s:%s] is not an instance of '\
                      'DomainMappingMatrix or MultipleDomainMatrix.'
        messages = []
        for i, row in enumerate(self.data):
            for j, cell in enumerate(row):
                if i == j:
                    if not isinstance(cell, (
                            DesignStructureMatrix, MultipleDomainMatrix)):
                        messages.append(message_dsm % (i, j))
                elif not isinstance(cell, (
                        DomainMappingMatrix, MultipleDomainMatrix)):
                    raise messages.append(message_ddm % (i, j))
        if messages:
            raise DSMError('\n'.join(messages))
