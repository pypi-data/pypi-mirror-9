######
TddMon
######

.. image:: https://pypip.in/wheel/tddmon/badge.svg
    :target: https://pypi.python.org/pypi/tddmon/
    :alt: Wheel Status

.. image:: https://pypip.in/version/tddmon/badge.svg
    :target: https://pypi.python.org/pypi/tddmon/
    :alt: Latest Version

.. image:: https://pypip.in/license/tddmon/badge.svg
    :target: https://pypi.python.org/pypi/tddmon/
    :alt: License


Goal
====

Help keeping Test Driven Development flow.

Installation
============

Install TddMon:

.. code-block:: console

   pip install tddmon

or current development version:

.. code-block:: console

   pip install hg+https:://bitbucket.org/kidosoft/tddmon

Usage
=====

.. code-block:: console

   tddmon -l test_run.log test_unit.py


In above example file `test_unit.py` will be run like any other
module so be sure to put `unittest.main()` or similar inside it.
tddmon will monitor all ".py" files inside current directory for changes in
modification time and run test whenever their change.

Monitored files will be measured for coverage. Test results will be logged
into log file (test_run.log in example) and on stdout you'll see
your working flow in TDD.

* red - one or more tests fail
* green - your tests has passed
* blue - consecutive run tests has passed; in most cases it means your refactoring your code.

If you want to limit files to measure coverage use .coveragerc
as described on coverage module page:
http://nedbatchelder.com/code/coverage/config.html


Documentation
=============

http://kidosoft.pl/docs/tddmon/

TODO
====

* option to separately logging test errors and coverage
* sending flow status and log results to remote server
