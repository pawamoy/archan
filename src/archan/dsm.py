# -*- coding: utf-8 -*-

"""
DSM module.

Contains the DesignStructureMatrix class.
"""

from .errors import DSMError


class DesignStructureMatrix(object):
    """Design Structure Matrix class."""

    def __init__(self, categories, entities, dependency_matrix,
                 framework='framework',
                 core_lib='core_lib',
                 app_lib='app_lib',
                 app_module='app_module',
                 broker='broker',
                 data='data'):
        """
        Initialization method.

        Args:
            categories (list): list of the names of the group of entities.
            entities (list): list of entities.
            dependency_matrix (list of list of int): 2-dim array.
            framework (str): name of framework group.
            core_lib (str): name of core_lib group.
            app_lib (str): name of app_lib group.
            app_module (str): name of app_module group.
            broker (str): name of broker group.
            data (str): name of data group.
        """
        # TODO - DSM: check compliance with DSM definitions and uses
        self.categories = categories
        self.entities = entities
        self.dependency_matrix = dependency_matrix
        self.size = len(dependency_matrix)

        self.framework = framework
        self.core_lib = core_lib
        self.app_lib = app_lib
        self.app_module = app_module
        self.broker = broker
        self.data = data

        cat_nb = len(categories)
        ent_nb = len(entities)
        rows = self.size
        columns = len(dependency_matrix[0])
        categories_names = (framework, core_lib, app_lib,
                            app_module, broker, data)
        if cat_nb != ent_nb:
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
        for i, category in enumerate(categories):
            if category not in categories_names:
                raise DSMError(
                    'Beware: category %s (in position %d) does not match '
                    'any valid category name (%s)' % (
                        category, i, ', '.join(categories_names)))
