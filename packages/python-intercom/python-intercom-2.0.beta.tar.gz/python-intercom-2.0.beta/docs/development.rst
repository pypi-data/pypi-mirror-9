Development
===========

Running the tests
-----------------

Run the unit tests:

::

    nosetests tests/unit

Run the integration tests:

::

    # THESE SHOULD ONLY BE RUN ON A TEST APP!
    INTERCOM_APP_ID=xxx INTERCOM_APP_API_KEY=xxx nosetests tests/integration

Generate the Documentation
--------------------------

::

    cd docs
    make html

Code coverage
-------------

Generate a code coverage report:

::

    nosetests --with-coverage --cover-package=intercom tests/unit


Runtime Dependencies
--------------------

* `Requests <http://python-requests.org/>`_ – an HTTP library “for human beings”
* `inflection <http://inflection.readthedocs.org/en/latest/>`_ – Inflection is a string transformation library. It singularizes and pluralizes English words, and transforms strings from CamelCase to underscored string.
* `six <https://bitbucket.org/gutworth/six>`_ – Six is a Python 2 and 3 compatibility library. It provides utility functions for smoothing over the differences between the Python versions with the goal of writing Python code that is compatible on both Python versions.
* `certifi <http://certifi.io/>`_ – Certifi is a carefully curated collection of Root Certificates for validating the trustworthiness of SSL certificates while verifying the identity of TLS hosts.

Development Dependencies
------------------------

* `nose <http://readthedocs.org/docs/nose/en/latest/>`_ – makes unit testing easier.
* `coverage <http://nedbatchelder.com/code/coverage/>`_ – code coverage.
* `mock <http://www.voidspace.org.uk/python/mock/>`_ – patching methods for unit testing.
* `Sphinx <http://sphinx.pocoo.org/>`_ – documentation decorator.


Authors
-------

.. include:: ../AUTHORS.rst
