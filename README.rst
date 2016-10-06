========
Overview
========

.. start-badges

|travis|
|codecov|
|landscape|
|version|
|wheel|
|gitter|

.. |travis| image:: https://travis-ci.org/Pawamoy/archan.svg?branch=master
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/Pawamoy/archan/

.. |codecov| image:: https://codecov.io/github/Pawamoy/archan/coverage.svg?branch=master
    :alt: Coverage Status
    :target: https://codecov.io/github/Pawamoy/archan/

.. |landscape| image:: https://landscape.io/github/Pawamoy/archan/master/landscape.svg?style=flat
    :target: https://landscape.io/github/Pawamoy/archan/
    :alt: Code Quality Status

.. |version| image:: https://img.shields.io/pypi/v/archan.svg?style=flat
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/archan/

.. |wheel| image:: https://img.shields.io/pypi/wheel/archan.svg?style=flat
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/archan/

.. |gitter| image:: https://badges.gitter.im/Pawamoy/archan.svg
    :alt: Join the chat at https://gitter.im/Pawamoy/archan
    :target: https://gitter.im/Pawamoy/archan?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge


.. end-badges

A Python module that analyses your achitecture strength based on DSM data.

Archan is a Python module that analyzes the strength of your
project architecture according to some criteria described in
"`The Protection of Information in Computer Systems`_", written by
Jerome H. Saltzer and Michael D. Schroeder.

.. _The Protection of Information in Computer Systems : https://www.cs.virginia.edu/~evans/cs551/saltzer/

Archan is used in combination with `dependenpy`_ in the Django app called
`django-meerkat`_.

.. _dependenpy: https://github.com/Pawamoy/dependenpy
.. _django-meerkat: https://github.com/Pawamoy/django-meerkat


License
=======

Software licensed under `MPL 2.0`_ license.

.. _BSD-2 : https://opensource.org/licenses/BSD-2-Clause
.. _MPL 2.0 : https://www.mozilla.org/en-US/MPL/2.0/

Installation
============

Just run ``pip install archan``.

Usage
=====

Archan takes a dependency matrix as parameter. It is a list of list of
numeric values, representing the dependencies between the packages
that are used in your project. It also needs the keys (one string for each
row of the matrix), and their associated
group type.

In django-meerkat, these data are provided by the dependenpy Python module,
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

    my_dsm = DesignStructureMatrix(my_groups, my_keys, my_matrix)
    archan = Archan()
    results = archan.check(dsm)
    print(results)


Documentation
=============

https://github.com/Pawamoy/archan.wiki

Development
===========

To run all the tests: ``tox``
