.. _installation:

Detailed Installation Instructions
==================================

SamSifter is written in Python3, so you need a working Python3 interpreter.
It requires the additional packages ``PyQt4`` to display the GUI, ``numpy``
for vectorized calculations, ``pandas`` for statistical summaries, and
``matplotlib`` to plot
optional coverage and read lengths distributions. The Python setup tools normally
take care of these requirements for you, however at time of writing the package
``PyQt4`` is not available in the
`PyPI repositories <http://https://pypi.python.org/pypi>`_ so you have to
install it using your operating system's package management.

If you already have a working Python3 installation with all required packages
you can skip the following section.

.. contents:: Contents

Installing ``Python3`` and ``PyQt4``
------------------------------------

Below you can find tested installation instructions for Debian-based
**GNU/Linux** distributions. The package names for other Linux distributions
should be very similar though. The **Windows** installation has only been tested
on a 32-bit Windows XP installation (currently the only test system available).
The installation instructions for **Mac OS X** are likely incomplete as they
could not be tested at all.

Debian 8 (jessie) and newer or Ubuntu 14.04 and newer
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The preparation of the SamSifter installation on Debian 8 (jessie)
and newer or Ubuntu 14.04 and newer is very simple as all packages are already
available in the standard repositories::

	sudo aptitude install python3 python3-dev python3-setuptools python3-nose python3-pyqt4 python3-numpy python3-matplotlib python3-pandas

You can now proceed with the actual SamSifter installation.

Older Debian or Ubuntu systems
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Older Debian/Ubuntu systems provide only a rudimentary Python3 environment
lacking the ``matplotlib`` package. We have to use the Python tools
``easy_install`` and ``pip`` to obtain it. The following steps have been tested
successfully on Ubuntu 12.04::

	# install Python3 system (as far as possible)
	sudo aptitude install python3 python3-dev python3-setuptools python3-nose python3-pyqt4 python3-numpy python3-tornado libfreetype6-dev
	# install pip for Python3
	sudo easy_install3 -U distribute
	sudo easy_install3 pip
	# matplotlib is not yet available, thus we install it from PyPI
	sudo pip3 install matplotlib==1.3.1
	# same for pandas
	sudo pip3 install pandas==0.14.1

You can now proceed with the actual SamSifter installation.

Mac OS X using Homebrew
^^^^^^^^^^^^^^^^^^^^^^^

Using `Homebrew <http://brew.sh>`_, the "missing package manager for OS X",
seems to be the easiest way to obtain an up to date ``Python3`` system including
``PyQt4`` on a Mac. Install ``Homebrew`` by pasting the following command into a
Terminal prompt::

	ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"

and follow the on-screen instructions. Once you have checked that the system is
functional with ::

	brew doctor

you can install these packages with the following commands (current versions at
time of release according to `Braumeister <http://braumeister.org/search>`_)::

	brew install python3        # current version: 3.4.2
	brew install pyqt           # current version: 4.11.3
	brew install pkg-config     # current version: 0.28

Open a fresh Terminal window, confirm that it uses the newly installed Python3
interpreter at `/usr/local/bin/python` by running ::

	which python

and continue to install additional Python packages with the built-in package
management::

	# install pip
	easy_install -U distribute
	easy_install pip
	# install setuptools, numpy and matplotlib
	pip install setuptools
	pip install numpy
	pip install matplotlib==1.3.1
	pip install pandas==0.14.1

You can now proceed with the actual SamSifter installation.

Windows (32 bit)
^^^^^^^^^^^^^^^^

For any Windows system the use of a packaged Python 3.4 distribution like ``Anaconda``
from http://continuum.io/downloads#all is recommended. However, if you'd rather
install the individual packages by yourself you can follow these steps.
The following instructions have been tested successfully on Windows XP (32 bit):

1. Download and install Python from https://www.python.org/downloads/windows/.
   The recommended version is
   `Python 3.4.2 <https://www.python.org/ftp/python/3.4.2/python-3.4.2.msi>`_.
   During installation, make sure to include ``pip`` in the installation and
   check the option to automatically add ``python.exe`` to your ``PATH``.

2. Download and install ``PyQt4`` from
   http://www.riverbankcomputing.com/software/pyqt/download.
   The recommended version is
   `PyQt 4.11.3 for Python 3.4 and Qt 4.8.6 <http://sourceforge.net/projects/pyqt/files/PyQt4/PyQt-4.11.3/PyQt4-4.11.3-gpl-Py3.4-Qt4.8.6-x32.exe>`_.

3. Download and install ``numpy`` from http://www.numpy.org/. The recommended
   version is
   `numpy 1.9.1 for Python 3.4 <http://downloads.sourceforge.net/project/numpy/NumPy/1.9.1/numpy-1.9.1-win32-superpack-python3.4.exe>`_.

4. Download and install ``matplotlib`` from http://www.matplotlib.org/. The
   recommended version is `matplotlib 1.4.0 for Python 3.4  <http://downloads.sourceforge.net/project/matplotlib/matplotlib/matplotlib-1.4.0/matplotlib-1.4.0.win32-py3.4.exe>`_.

5. Download and install ``pandas`` from
   http://www.lfd.uci.edu/~gohlke/pythonlibs/#pandas. The recommended version is
   ``pandas`` 0.15.2 for Python 3.4.

You can now proceed with the actual SamSifter installation.

Installing SamSifter
--------------------

Once you have a working Python3 environment use an administrator account to
download and install the current SamSifter package on your system with the
command::

	pip3 install SamSifter

Previous versions will be uninstalled automatically. The installation can be
tested with ::

	samsifter --help

If everything went fine you should see the following help text::

	usage: samsifter [-h] [-v] [-d]

	SamSifter helps you create filter workflows for next-generation sequencing
	data. It is primarily used to process SAM files generated by MALT prior to
	metagenomic analysis in MEGAN.

	optional arguments:
	  -h, --help     show this help message and exit
	  -v, --verbose  print additional information to stderr
	  -d, --debug    show debug options in menu

Starting the program without any arguments will display the GUI and let you
edit your first workflow.

Uninstalling SamSifter
----------------------

To get rid of SamSifter simply execute the following command as administrator::

	pip3 uninstall SamSifter

The Python utility ``pip3`` will list all currently installed
available versions for selective removal. Proceed similarly with any required
packages (e.g. ``matplotlib``) if you don't need them anymore.