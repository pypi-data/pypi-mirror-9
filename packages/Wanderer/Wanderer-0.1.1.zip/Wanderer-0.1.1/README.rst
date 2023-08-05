.. image:: https://travis-ci.org/danbradham/wanderer.svg
  :target: https://travis-ci.org/danbradham/wanderer
  :alt: Build Status


.. image:: https://coveralls.io/repos/danbradham/wanderer/badge.png
  :target: https://coveralls.io/r/danbradham/wanderer
  :alt: Coverage Status

.. image:: https://img.shields.io/badge/pypi-0.1.0-brightgreen.svg
    :target: https://testpypi.python.org/pypi/wanderer/
    :alt: Latest Version

========
Wanderer
========
Roaming CG Production

Bootstrap a full cg production pipeline that remains completely relative to its root directory. Making Wanderer the perfect choice for offsite/distributed production.


Road Map
========

* API for managing your project

  * ``Wanderer`` : Main application object manages everything
  * ``Context`` : Information about the current situation
    e.g.(Maya>Project>Sequence>Shot>Animation)

  * ``Event`` : Emitted by in a context
  * ``Action`` : Handles an event emitted in select contexts

* User Interface

  * Cross-application user interface to control Wanderer project
  * Makes used of ``Wanderer`` to browse and modify a project.

* Command Line Interface

  * bootstrap: create a new project from a simple configuration file
  * launch: launch an application in a context
  * configure: pops up a PySide UI for modifying your Wanderer base config or a Wanderer project config.
  * pip: Deploy python packages to individual projects
  * *docs: takes you directly to this documentation*
  * *filetools: create/modify/delete sequences of files*


Get Wanderer
============

PyPi
----
Wanderer is available through the python package index as **wanderer**.

::

    pip install wanderer

Distutils/Setuptools
--------------------

::

    git clone git@github.com/danbradham/wanderer.git
    cd wanderer
    python setup.py install


Documentation
=============

For more information visit the `docs <http://wanderer.readthedocs.org>`_.
