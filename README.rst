Archan
======

.. image:: https://pypip.in/version/archan/badge.svg
    :target: https://pypi.python.org/pypi/archan/
    :alt: Latest Version

.. image:: https://pypip.in/status/archan/badge.svg
    :target: https://pypi.python.org/pypi/archan/
    :alt: Development Status

.. image:: https://pypip.in/format/archan/badge.svg
    :target: https://pypi.python.org/pypi/archan/
    :alt: Download format

.. image:: https://travis-ci.org/Pawamoy/archan.svg?branch=master
    :target: https://travis-ci.org/Pawamoy/archan
    :alt: Build Status

.. image:: https://readthedocs.org/projects/archan/badge/?version=latest
    :target: https://readthedocs.org/projects/archan/?badge=latest
    :alt: Documentation Status

.. image:: https://coveralls.io/repos/Pawamoy/archan/badge.svg?branch=master
    :target: https://coveralls.io/r/Pawamoy/archan?branch=master
    :alt: Coverage Status

.. image:: https://landscape.io/github/Pawamoy/archan/master/landscape.svg?style=flat
   :target: https://landscape.io/github/Pawamoy/archan/master
   :alt: Code Health

.. image:: https://pypip.in/py_versions/archan/badge.svg
    :target: https://pypi.python.org/pypi/archan/
    :alt: Supported Python versions

.. image:: https://pypip.in/license/archan/badge.svg
    :target: https://pypi.python.org/pypi/archan/
    :alt: License

Archan is a Python module that analyzes the strength of your project architecture
according to some criteria described in
"`The Protection of Information in Computer Systems`_", written by
Jerome H. Saltzer and Michael D. Schroeder.

.. _The Protection of Information in Computer Systems : https://www.cs.virginia.edu/~evans/cs551/saltzer/

Archan is used in combination with `dependenpy`_ in the Django app called
`django-archan`_.

.. _dependenpy: https://github.com/Pawamoy/dependenpy
.. _django-archan: https://github.com/Pawamoy/django-archan

Installation
------------

Just run ``pip install archan``.

Usage
-----

Archan takes a dependency matrix as parameter. It is a list of list of numeric values,
representing the dependencies between the packages that are used in your project.
It also needs the keys (one string for each row of the matrix), and their associated
group type.

In django-archan, these data are provided by the dependenpy Python module,
but you can build and use your own:

.. code:: python

    from archan.dsm import DesignStructureMatrix
    from archan.checker import Archan

    my_matrix = [[0, 1, 2, 0],
                 [1, 1, 1, 0],
                 [0, 0, 0, 3],
                 [3, 3, 0, 1]]

    my_keys = ['core', 'some_app', 'whatever', 'feature']
    my_groups = ['core_lib', 'app_module', 'app_module', 'app_module']

    archan = Archan()
    my_dsm = DesignStructureMatrix(my_groups, my_keys, my_matrix)

    complete_mediation = archan.check_complete_mediation(my_dsm)
    economy_of_mechanism = archan.check_economy_of_mecanism(my_dsm)
    ...

Please take a look at the source code to see what other methods are available.

License
-------

Copyright (c) 2015 Pierre Parrend

This Source Code is subject to the terms of the Mozilla Public
License, v. 2.0. See the LICENSE.txt file for more details.