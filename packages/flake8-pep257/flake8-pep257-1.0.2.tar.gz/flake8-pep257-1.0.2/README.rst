=============
flake8-pep257
=============

This is just a simple flake8 plugin for the `pep257 <https://github.com/GreenSteam/pep257>`_ Python utility for
validating docstrings.

* Python 2.6, 2.7, PyPy, PyPy3, 3.3, and 3.4 supported on Linux and OS X.
* Python 2.7, 3.3, and 3.4 supported on Windows (both 32 and 64 bit versions of Python).

.. image:: https://img.shields.io/appveyor/ci/Robpol86/flake8-pep257/master.svg?style=flat-square&label=AppVeyor%20CI
   :target: https://ci.appveyor.com/project/Robpol86/flake8-pep257
   :alt: Build Status Windows

.. image:: https://img.shields.io/travis/Robpol86/flake8-pep257/master.svg?style=flat-square&label=Travis%20CI
   :target: https://travis-ci.org/Robpol86/flake8-pep257
   :alt: Build Status

.. image:: https://img.shields.io/codecov/c/github/Robpol86/flake8-pep257/master.svg?style=flat-square&label=Codecov
   :target: https://codecov.io/github/Robpol86/flake8-pep257
   :alt: Coverage Status

.. image:: https://img.shields.io/pypi/v/flake8-pep257.svg?style=flat-square&label=Latest
   :target: https://pypi.python.org/pypi/flake8-pep257/
   :alt: Latest Version

.. image:: https://img.shields.io/pypi/dm/flake8-pep257.svg?style=flat-square&label=PyPI%20Downloads
   :target: https://pypi.python.org/pypi/flake8-pep257/
   :alt: Downloads

`Quickstart`_
=============

Install:

.. code:: bash

    pip install flake8-pep257

Run:

.. code:: bash

    flake8

`Error Codes`_
==============

List of error codes are available here: http://pep257.readthedocs.org/en/latest/error_codes.html

`Configuration`_
================

Settings may be specified in ``tox.ini`` (under the ``[flake8]`` or ``[pep257]`` sections), ``setup.cfg``, and/or
``.pep257``. Refer to `this page <http://pep257.readthedocs.org/en/latest/usage.html>`_ for more information.

When specifying settings in ``tox.ini`` under the ``[flake8]`` section, use ``show-source`` instead of ``source`` and
``show-pep257`` instead of ``explain``.

`Changelog`_
============

This project adheres to `Semantic Versioning <http://semver.org/>`_.

`1.0.2 - 2015-04-04`_
---------------------

* Fixed setup.py requirements bug.

`1.0.0 - 2015-04-04`_
---------------------

* Initial release.
