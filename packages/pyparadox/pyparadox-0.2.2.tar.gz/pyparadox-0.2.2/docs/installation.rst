============
Installation
============

PyParadox requires Python 3, pip and PyQt5. The ways of obtaining these three
pieces of software differ per platform.

Linux
-----

You probably already have Python installed. You may not, however, have pip yet.
To check whether you have pip, you can simply enter ``pip`` into the terminal.
If it returns anything other than ``pip: command not found``, you're good to
go. If it does say that pip wasn't found, you'll want to install your
distribution's pip package. For Ubuntu, this would look like this::

    sudo apt-get install python3-pip

Additionally, you'll want to have PyQt5 installed. Most distributions should
also be able to provide you with a version of PyQt5. The Ubuntu installation
looks like this::

    sudo apt-get install python3-pyqt5

Now that you've satisfied the dependencies of PyParadox, you can download and
install it. This should be as easy as::

    sudo pip install pyparadox

If PyParadox installed correctly, the :doc:`Usage <usage>` section should be
able to help you next.

OS X
----

OS X installation is a little tricky, because Apple provides its own version of
Python that should be very much left alone. You do not want to mess around with
this version of Python, ever. Never mind the fact that OS X's version of Python
is too outdated to run PyParadox.

The best way to install PyParadox under OS X is to make a separate Python
installation from Apple's version. But because I do not have access to a Mac,
I cannot provide succinct (and working) instructions on how to achieve a
full working installation of PyParadox and its dependencies.

Windows
-------

This should be about as easy as the Linux instructions. Simply download and
install Python and PyQt5. Python can be downloaded from `the official Python
downloads page <https://www.python.org/downloads/>`_ and PyQt5 can be
downloaded from the `Riverbank Computing downloads page
<http://www.riverbankcomputing.com/software/pyqt/download5>`_.

After these two components are installed, open up a command line interface. In
Windows, this is more commonly referred to as ``cmd.exe``. There are various
ways of accessing this program, but by far the most convenient ways to get
there are:

* Right-clicking on your start menu button and clicking ``Command Prompt``.
* Searching through your programs from ``cmd.exe``.

  - Under Windows 8 this means typing ``cmd.exe`` on the Modern UI start
    screen, and watching the results pop up on the right side of the screen.

  - Under Windows 7, this means opening up your start menu and typing
    ``cmd.exe`` into the search box.

After the console is opened, type the following line into the console and hit
enter::

    pip install pyparadox

After this, you should be all set, and :doc:`Usage <usage>` should be able
to help you out further.
