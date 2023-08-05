Checkers
--------

A checker provides testing functionalities. It is run by the narvalbot and
multiple checkers can be called in a recipe. Its return status can be
"success" if the test passed, "skipped" if the test is skipped, a "failure" if
the test failed or an "error" if the test could not be run to completion (maybe
the environment could not be set up or the test program was badly written).

Apycot comes with several checkers described below. If you do not find the
checker you are looking for, write your own by deriving an existing one and
contribute it back to the apycot project ;).

Some checkers depend on third-party programs (usually a Python package or
an external command) and may not be available on your system.

Once the narval-apycot package is installed on the same machine as the bot, the
checkers can be accessed by the Narval bot.

Running generic test files
++++++++++++++++++++++++++

script_runner
~~~~~~~~~~~~~

TODO

Debian packaging
++++++++++++++++

lintian
~~~~~~~

TODO

Javascript
++++++++++

jslint
~~~~~~

TODO

For Python code
+++++++++++++++

python_syntax
~~~~~~~~~~~~~
:extensions: .py
:description:
  Checks the syntax of Python files using the compile function coming with
  Python.

pytest
~~~~~~

TODO

pyunit
~~~~~~
:depends on: pyunit
:description:
  Execute tests found in the "test" or "tests" directory of the package. The check
  succeed if no test cases failed. Note each test module is executed by a spawed
  python interpreter and the output is parsed, so tests should use the default
  text output of the unittest framework, and avoid messages on stderr.
  
  +-----------------------------+------+--------------------------------------+
  |   name                      | req. |   description                        |
  +=============================+======+======================================+
  | coverage                    |  no  | Enable or disable coverage test (0   |
  |                             |      | or 1, default to 1 when devtools is  |
  |                             |      | available)                           |
  +-----------------------------+------+--------------------------------------+
  | test_dirs                   |  no  | List of comma separated candidates   |
  |                             |      | of tests directory. default to       |
  |                             |      | "test, tests"                        |
  +-----------------------------+------+--------------------------------------+

pycoverage
~~~~~~~~~~

:depends on: devtools_
:description:
  When devtools is available, test will be launched in a coverage mode. This test
  will gather coverage information, and will succeed if the test coverage is
  superior to a given treshold. *This checker must be executed after the
  pyunit checker.*
:options:
  +--------------------+-------+--------------------------------------------------+
  |   name             |  req. |   description                                    |
  +====================+=======+==================================================+
  | coverage_threshold |  yes  | the minimal note to obtain for the test coverage |
  +--------------------+-------+--------------------------------------------------+


pylint
~~~~~~

:depends on: pylint_
:description:
  Use Pylint to check a score for python package. The check fails if the score is
  inferior to a given treshold.
:options:
  +---------------------+--------+-------------------------------------------+
  |        name         |  req.  |   description                             |
  +=====================+========+===========================================+
  | pylint_threshold    |   no   | the minimal note to obtain for the        |
  |                     |        | package from PyLint                       |
  +---------------------+--------+-------------------------------------------+
  | show_categories     |   no   | comma separated list of letter used to    |
  |                     |        | filter the message displayed default to   |
  |                     |        | Error and Fatal                           |
  +---------------------+--------+-------------------------------------------+
  | pylintrc            |   no   | The path to a pylint configuration file   |
  +---------------------+--------+-------------------------------------------+

pychecker
~~~~~~~~~

TODO

py.test
~~~~~~~

TODO
