#######
Testing
#######

This package was tested using `pytest`_, `tox`_.  Each suite of tests
runs the `coverage`_ for reporting metrics on how much of the package
was tested.


Setup
-----

To run the tests, some packages should be installed previously.  They can be
installed using:

.. code-block:: bash

    pip install .[tests]

On occasion, the shell does not immediately register tox.  This can be fixed
using:

.. code-block:: bash

    hash -r

The :envvar:`WORKON_HOME` environment variable should be setup to
avoid polluting the current directory with a large number of virtual
environment folders.


Executing
---------

To run all major tests, simply run:

.. code-block:: bash

    tox



Environments
------------

To list the available environments:

.. code-block:: bash

    tox -l


The following tox environments are available:

Suites
******
* py27 -- suite of tests using `python 2.7`_  (currently python 2.7.12)
* py35 -- suite of tests using `python 3.5`_  (currently python 3.5.2)
* pypy -- suite of tests using `pypy`_  (currently pypy 5.3.0)


Subset Testing
**************

On occassion it may make sense to run just a subset of tests.  This can
be accomplished with any of the following.  Any of these may be prefaced
by one of the suites if a specific interpreter is required.  Otherwise
the default interpreter will be used.  For example, to run the smoke
tests on `python 3.5`_, use:  :command:tox -e py35-smoke

* smoke -- fast running smoke tests
* unit -- full set of unit tests
* integration -- uses a live system, so connectivity must be available
* requirements -- uses the `requirements.txt` file within the repo to install a specific set of libraries


Extra Testing
*************

Two additional sets of tests have been provided to adhere to style and
license requirements:

* license -- checks for permissive left copy licenses
* style -- checks for adherence to :pep:`8` using `flake8`_ linter.


Utilities
*********

Additional environments are provided within tox for utility functions
including cleaning, coverage reporting, and pushing to the pypi repo.

The following environments are available:

* clean -- removes previous testing results
* coverage-report -- generates the current coverage
* push -- creates a build and pushes it to the pypi server
* release -- creates a build and pushes it to the pypi server

Note that release should always be performed from the master branch and
push should always be performed from the develop branch.


.. Python interpreters
.. _python 2.7: https://www.python.org/download/
.. _python 3.5: https://www.python.org/download/
.. _pypy: http://pypy.org/download.html

.. Python packages
.. _coverage: https://pypi.python.org/pypi/coverage
.. _detox: https://pypi.python.org/pypi/detox
.. _flake8: https://pypi.python.org/pypi/flake8
.. _pytest: https://pypi.python.org/pypi/pytest
.. _tox: https://testrun.org/tox/latest/
