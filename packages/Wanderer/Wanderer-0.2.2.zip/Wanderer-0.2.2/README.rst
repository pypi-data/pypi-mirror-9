.. image:: https://travis-ci.org/danbradham/Wanderer.svg?branch=master
    :target: https://travis-ci.org/danbradham/Wanderer
    :alt: Build Status

.. image:: https://pypip.in/version/wanderer/badge.svg
    :target: https://pypi.python.org/pypi/wanderer/
    :alt: Latest Version

========
Wanderer
========
Roaming CG Production

Bootstrap a full cg production pipeline that remains completely relative to its root directory. Making Wanderer the perfect choice for offsite/distributed production.


Features
========

* Per-project Configurations

  * Platform agnostic
  * Shareable
  * Replaceable

* Powerful Command Line Interface

  * bootstrap: create a new project from a configuration
  * launch: launch applications in project specific environments
  * install/uninstall: use pip to install/uninstall packages per project
  * docs: opens documentation in your web browser
  * filetools: create/modify/delete sequences of files


Planned Features
================

* API for managing your project

  * ``Wanderer`` : Main application object manages everything
  * ``Context`` : Information about the current situation
    e.g.(Maya>Project>Sequence>Shot>Animation)

  * ``Event`` : Emitted by in a context
  * ``Action`` : Handles an event emitted in select contexts

* User Interface

  * Cross-application user interface to control a Wanderer project

* Command Line Interface

  * config: get and set values in your configuration


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

    git clone git@github.com:danbradham/wanderer.git
    cd wanderer
    python setup.py install


Documentation
=============

For more information visit the `docs <http://wanderer.readthedocs.org>`_.
