Contribution
============

If you like to contribute to this project please read the following guides.

Django Code
-----------

To install all requirements for development and testing, you can use the provided
requirements file.

.. code-block:: bash

    $ make devinstall

Testing the code
````````````````

`django-livewatch` uses ``py.test`` for testing. Please ensure that all tests pass
before you submit a pull request. ``py.test`` also runs PEP8 and PyFlakes checks
on every run.

This is how you execute the tests and checks from the repository root directory.

.. code-block:: bash

    $ make tests

If you want to generate a coverage report, you can use the following command.

.. code-block:: bash

    $ make coverage

Or if you want to generate a HTML version of the coverage report, use the following command.

.. code-block:: bash

    $ make coverage-html

The generated HTML files are located in the ``htmlcov`` folder.

Documentation
`````````````

`django-livewatch` uses Sphinx for documentation. You find all the source files
in the ``docs/source`` folder.

To update/generate the HTML output of the documentation, use the following
command:

.. code-block:: bash

    $ make docs

Please make sure that you don't commit the build files inside ``docs/build``.
