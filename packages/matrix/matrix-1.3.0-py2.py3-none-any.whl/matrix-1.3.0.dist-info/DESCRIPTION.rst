===============================
matrix
===============================

.. image:: http://img.shields.io/travis/ionelmc/python-matrix/master.png
    :alt: Travis-CI Build Status
    :target: https://travis-ci.org/ionelmc/python-matrix

.. image:: https://ci.appveyor.com/api/projects/status/tqvpgkg5d33vnknh/branch/master
    :alt: AppVeyor Build Status
    :target: https://ci.appveyor.com/project/ionelmc/python-matrix

.. image:: http://img.shields.io/coveralls/ionelmc/python-matrix/master.png
    :alt: Coverage Status
    :target: https://coveralls.io/r/ionelmc/python-matrix

.. image:: http://img.shields.io/pypi/v/matrix.png
    :alt: PYPI Package
    :target: https://pypi.python.org/pypi/matrix

.. image:: http://img.shields.io/pypi/dm/matrix.png
    :alt: PYPI Package
    :target: https://pypi.python.org/pypi/matrix

Generic matrix generator.

* Free software: BSD license

Installation
============

::

    pip install matrix

Documentation
=============

https://python-matrix.readthedocs.org/

Development
===========

To run the all tests run::

    tox


Changelog
=========

1.3.0 (2015-04-15)
------------------

* Added an optional ``[cli]`` extra (use ``pip install matrix[cli]``) that enables a ``matrix-render`` command. 
  The new command loads configuration and passes the generated matrix to the given Jinja2 templates.

1.2.0 (2015-04-03)
------------------

* Fix handling when having aliased entries that have empty ("-") values.

1.1.0 (2015-02-12)
------------------

* Add support for empty inclusions/exclusions.

1.0.0 (2014-08-09)
------------------

* Fix Python 2.6 support.
* Add support for really empty entries (leave completely empty instead of "-")


0.5.0 (2014-08-09)
------------------

* Fix Python 3 support.


