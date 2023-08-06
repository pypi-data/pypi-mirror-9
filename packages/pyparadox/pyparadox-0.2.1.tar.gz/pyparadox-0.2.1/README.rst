===============================
PyParadox
===============================

.. image:: https://img.shields.io/pypi/v/pyparadox.svg
        :target: https://pypi.python.org/pypi/pyparadox


PyParadox is a nix launcher for Paradox titles.

* Free software: GPLv3+
* Documentation: https://pyparadox.readthedocs.org.
* Source code: https://gitlab.com/carmenbbakker/pyparadox
* PyPI: https://pypi.python.org/pypi/pyparadox

Features
--------

* Cross-platform: Linux, OS X and Windows.
* Supports Python 3.3+ with PyQt5.
* Games: PyParadox supports all cross-platform grand strategy titles of
  Paradox Interactive that use the Clausewitz engine. To date, these include:
  - Crusader Kings II
  - Europa Universalis IV
* Steam: PyParadox can be launched from Steam when starting the title from the
  Steam interface. All Steam integration should work just fine. A small
  configuration inside Steam is required to make sure that PyParadox is used
  instead of the stock launcher. See the documentatation on how to set this up.
* PyParadox separates the expansion DLCs from the regular DLCs. This should
  make it easier to start up your game with the exact expansions you want.
* PyParadox fixes an anomaly under Linux that causes the game to mess with
  the screen resolution when alt+tabbing. This anomaly was introduced when
  Paradox released their (new) stock launcher for Linux. By bypassing this
  launcher, PyParadox also bypasses the anomaly.
