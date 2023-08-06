.. :changelog:

History
-------

0.2.2 (2015-04-12)
--------------------

* Patched a bug that caused PyParadox to fail to launch from Steam.
* Removed Python 2.7 support from PyPI.

0.2.1 (2015-04-11)
--------------------

* Minor patches to documentation because apparently I can't release anything
  without messing that stuff up.

0.2.0 (2015-04-11)
---------------------

* Complete rewrite of the project, with reuse of some code.
* Now no longer supports Python 2.7 and Qt 4. This program will only work with
  Python 3.3+ and PyQt5.
* Configuration files relocated to a different location. Old configuration
  files no longer valid.
* Graphical user interface makes use of Qt .ui files, rather than hardcoded
  QtGui/QtWidgets code.
* A lot of functionality has been decoupled from the user interface. While the
  UI code performs *some* glue logic, it should be relatively trivial to cook
  up a user interface in a different framework. An experimental QML front-end
  is under consideration.
* Unit tests are a lot leaner, using fewer mocks and patches, instead relying
  much more on dependency injection.
* Documentation rewritten.

0.1.3 (2015-01-31)
---------------------

* Added --pyqt4 argument to force the usage of PyQt4.
* Fixed PyQt4 compatibility issues.

0.1.2 (2014-07-20)
---------------------

* Fixed typo that caused README to display incorrectly.

0.1.1 (2014-07-20)
---------------------

* Sweetened up the README with images of the program.

0.1.0 (2014-07-20)
---------------------

* Added descriptive error message when game fails to run.
* Added experimental PyQt4 support.
* Detailed installation instructions per platform added.
* A logo of each game is now displayed.
* Mods and DLCs are now sorted.
* The application now has an icon.

0.0.2 (2014-07-13)
---------------------

* Windows compatibility added.
* Window titles set correctly.
* Small UI tweaks (alt-shortcuts).
* Better game process management.
* Better unit testing, though incomplete.
* Just general code refactoring.
* Tested on Kubuntu 14.04 and Windows 8.1.  Still not sure about OS X.

0.0.1 (2014-07-10)
---------------------

* First release on PyPI.
* Basic functionality.  No polish yet.
* Only tested on Kubuntu 14.04.
