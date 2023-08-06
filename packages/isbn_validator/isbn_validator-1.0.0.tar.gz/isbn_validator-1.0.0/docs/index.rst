ISBN validator
==============

This module provides basic API for validation of the ISBN-10 and ISBN-13
numbers. It can also compute the checksum digits for incomplete numbers.

Examples
--------

::

    >>> import isbn_validator

ISBN validation::

    >>> isbn_validator.is_valid_isbn("80-85892-15-4")
    True
    >>> isbn_validator.is_valid_isbn("978-80-86056-31-9")
    True
    >>> isbn_validator.is_valid_isbn("978-80-904248-2-77777")
    False

Or just specific ISBN standard::

    >>> isbn_validator.is_isbn10_valid("80-85892-15-4")
    True
    >>> isbn_validator.is_isbn13_valid("978-80-86056-31-9")
    True

You can also let the module to compute the checksum digit::

    >>> isbn_validator.get_isbn10_checksum("80-86056-31")
    7
    >>> isbn_validator.get_isbn13_checksum("978-80-904248-2")
    1

API
---

.. toctree::
    :maxdepth: 1

    /api/isbn_validator.rst

Source code
-----------
This project is released as opensource (GPL) and source codes can be found at
GitHub:

- https://github.com/edeposit/edeposit.amqp.ltp

Installation
++++++++++++
Module is hosted at `PYPI <https://pypi.python.org/pypi/isbn_validator>`_,
and can be easily installed using
`PIP <http://en.wikipedia.org/wiki/Pip_%28package_manager%29>`_::

    sudo pip install isbn_validator

Testing
-------
Almost every feature of the project is tested in unit/integration tests. You
can run this tests using provided ``run_tests.sh`` script, which can be found
in the root of the project.

Requirements
++++++++++++
This script expects that pytest_ is installed. In case you don't have it yet,
it can be easily installed using following command::

    pip install --user pytest

or for all users::

    sudo pip install pytest

.. _pytest: http://pytest.org/


Example
+++++++
::

    $ ./run_tests.sh 
    ============================= test session starts ==============================
    platform linux2 -- Python 2.7.6 -- py-1.4.26 -- pytest-2.6.4
    collected 6 items 

    tests/test_isbn_validator.py ......

    =========================== 6 passed in 0.02 seconds ===========================

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`