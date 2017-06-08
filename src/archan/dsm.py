# -*- coding: utf-8 -*-

"""
DSM module.

Contains the DesignStructureMatrix class.
"""

from .errors import DSMError


class DSM(object):
    """Design Structure Matrix class."""

    def __init__(self, data, entities, categories=None):
        """
        Initialization method.

        Args:
            data (list of list of int): 2-dim array.
            entities (list): list of entities.
            categories (list): list of the names of the group of entities.
        """
        # TODO - DSM: check compliance with DSM definitions and uses
        if categories is None:
            self.categories = []
        else:
            self.categories = categories
        self.entities = entities
        self.data = data
        self.size = len(data)

        cat_nb = len(self.categories)
        ent_nb = len(entities)
        rows = self.size
        columns = len(data[0])
        if categories is not None and cat_nb != ent_nb:
            raise DSMError(
                'Beware: nb of categories: %s != nb of entities: %s' % (
                    cat_nb, ent_nb))
        if rows != columns:
            raise DSMError(
                'Beware: nb of rows: %s != nb of columns: %s in DSM matrix' % (
                    rows, columns))
        if ent_nb != rows:
            raise DSMError(
                'Beware: nb of entities: %s != nb of rows: %s' % (
                    ent_nb, rows))
