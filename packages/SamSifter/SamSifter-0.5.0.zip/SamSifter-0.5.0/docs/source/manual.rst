.. _manual:

================
SamSifter Manual
================

.. contents:: Contents

.. _installation:

Detailed Installation Instructions
==================================

SamSifter is written in Python3, so it runs on Windows, Mac OS X and GNU/Linux
as long as you have installed a working Python3 interpreter.
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

.. _edit_workflows:

Creating and Editing Workflows
==============================

Workflows are displayed and edited in the central part of the SamSifter window:

.. image:: _images/example_workflow.png
	:scale: 50%
	:alt: The workflow editor with an example workflow to filter SAM files for
	      ancient human pathogens.
	:align: center
	:target: _images/example_workflow.png

A workflow consists of three parts:

* An input file in SAM or BAM format (optionally zipped) which can be 
  specified in the upper part of the main window.
* A list of one or more tools and filters that are executed in a specific order.
  They are shown in the central part of the main window and can be freely
  rearranged, added and removed.
* An output file in SAM or BAM format (again optionally zipped to save space),
  which similar to the input file can be specified in the lower part of the main
  window. This part also contains options to enable the generation of RMA files
  for MEGAN.

When working with SamSifter for the first time all of these fields and lists 
will be empty and waiting for you. To get back to this pristine state simply
click the **[New]** button to create a new empty workflow. Any changes to your
current workflow will be discarded unless you follow the prompt to save them.

.. seealso:: :ref:`save_workflows`

We'll now take a closer look at each of these three parts.

Selecting an Input File
-----------------------
SamSifter supports input files in the SAM or BAM format, both compressed or
uncompressed. Some of the filters included in SamSifter may have additional
requirements for the sort order of the reads or optional annotations like
headers and MD tags. The input file can either be determined by typing the full
path into the text field or by clicking the **[Open...]** button and selecting
the file using a standard file open dialog.

SamSifter automatically checks if the file a) exists, b) is readable and c) has
the correct file type. The text field containing the file path will be
highlighted in orange to show you if any of these conditions are not fulfilled.
Hovering the mouse cursor over the text field shows a tooltip with hints how
to resolve the error.

.. image:: _images/input_error.png
	:scale: 50%
	:alt: An incomplete filename causes input errors that are shown by orange
	      highlighting and tooltips.
	:align: center
	:target: _images/input_error.png

Adding and Removing a Tool or Filter
------------------------------------
SamSifter includes a variety of filters and tools that can be used to process
your input file. You can add one to the workflow by selecting it from either the
**[Edit] > [Add Filter...]** menu or double-clicking an entry in the
**Filters and Tools** dock.

.. image:: _images/filters_dock.png
	:scale: 50%
	:alt: The Filters and Tools dock lists all available filters and tools by
	      category. Press F2 to show it or activate it in the **[View]** menu.
	:align: center
	:target: _images/filters_dock.png
	
You can toggle the dock on and off by pressing F2 or activating it in the
**[View]** menu.

The new entry is added to the currently selected row of your workflow or
appended to the end if no row is selected. To remove the entry click
**[Edit] > [Delete]** or press the Delete key.

Rearranging Tools and Filters
-----------------------------
The order of steps in the workflow can be freely rearranged by selecting any
entry and moving it up or down. To move an entry click **[Edit] > [Move up]** /
**[Edit] > [Move down]**, click the corresponding toolbar buttons, or use the
keyboard shortcuts Ctrl+Up and Ctrl+Down.

SamSifter validates the entire workflow after each change. Individual steps
in the workflow may have specific requirements for the type of input they accept
and/or the type of output they produce. If any of these requirements are not
fulfilled the color of the corresponding entry will change to orange and a
message will appear in the **Messages** dock with hints on how to resolve these
errors.

.. image:: _images/messages_dock.png
	:scale: 50%
	:alt: The Messages dock shows error messages and hints on how to resolve
	      them. Press F3 to show it or activate it in the **[View]** menu.
	:align: center
	:target: _images/messages_dock.png

You can toggle the dock on and off by pressing F3 or activating it in the
**[View]** menu.

Displaying and Editing Filter Settings
--------------------------------------
Most tools and filters in your workflow have settings that are required for the
tool to function properly as well as optional settings that can tweak the
functionality. The **Filter Settings** dock serves to show these settings along
with a description of the tool and a summary of its input and output
requirements.

.. image:: _images/settings_dock.png
	:scale: 50%
	:alt: The Filter Settings dock shows error messages and hints on how to
		  resolve them. Press F4 to show it, or activate it in the **[View]**
		  menu, or double-click any workflow entry.
	:align: center
	:target: _images/settings_dock.png

You can toggle the dock on and off by pressing F4, activating it in the
**[View]** menu or simply double-clicking the workflow step you are interested
in. The individual settings have tooltips that provide more information on their
meaning and effect.

.. seealso:: The available options depend on the tool or filter. Please see
             :ref:`filter_manuals` for details.

Selecting an Output File
------------------------
SamSifter supports output files in the SAM and BAM formats, both compressed and
uncompressed. The output file can either be determined by typing the full
path into the text field or by clicking the **[Save as...]** button and selecting
the new filename using a standard file save dialog.

Similar to the input field, the program automatically checks if the target
directory a) exists, b) is readable and c) if the new file has the correct file
type. The text field containing the file path will be highlighted in orange to
show you if any of these conditions are not fulfilled. Hovering the mouse cursor
over the text field shows a tooltip with hints how to resolve the error.

.. image:: _images/output_error.png
	:scale: 50%
	:alt: A non-existing directory causes output errors that are shown by orange
	      highlighting and tooltips.
	:align: center
	:target: _images/output_error.png

Optional: Creating an RMA file for MEGAN
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
SamSifter can automatically create a RMA file from SAM output files if a recent
version of MEGAN (version 5.8.3 or newer) including the SAM2RMA tool is
installed on your computer. The tool can be configured by clicking the
**[Settings...]** button.

.. image:: _images/sam2rma_dialog.png
	:scale: 50%
	:alt: The SAM2RMA dialog is used to change the settings for RMA file
	      creation.
	:align: center
	:target: _images/sam2rma_dialog.png

For details on the effect of the individual setting see the MEGAN manual or the
SAM2RMA help function. Clicking the **[Restore defaults]** button will revert
your changes to the default settings.
	
.. note:: The default settings here are recommended by the Krause Lab and may
          differ from the MEGAN default settings!
          
If the path to the SAM2RMA binary is highlighted orange you may have to update
the installation path or change the file permissions to make the program
executable.

.. _execute_workflows:

Executing Workflows
===================

Once a workflow is properly set up with input file, a list of tools or filters
to run and an output file you can run the entire workflow on your computer.

.. seealso:: :ref:`bash_export` if you'd like to process more than one file at a
             time or run the workflow using the command line of another
             computer.

Running a Workflow
------------------
To run a workflow simply click the **[Run]** button in the toolbar or choose
**[Run] > [Run]** from the menu. This button may be disabled in two situations:

* if your workflow has errors that need to be addressed -> take a closer look at
  entries with orange highlighting to resolve the errors, then try again.
* if another workflow is currently being processed -> wait for it to finish or
  click **[Stop]** to stop it, then try again.

Log Messages
------------
Once the workflow is being executed the **[Messages]** dock will pop up and show
a bunch of messages:

.. image:: _images/workflow_progress.png
	:scale: 50%
	:alt: A workflow produces messages to inform about warnings and errors.
	:align: center
	:target: _images/workflow_progress.png

Depending on your workflow and settings there will be

* Status messages in black, eg. the current status and process ID.
* Info messages in green; they're enabled by default but can be disabled for
  each step by disabling the individual ``verbose`` options if you don't like
  the noise.
* Warnings in yellow; they're usually harmless and SamSifter will continue to
  process the workflow but you may want to review these warnings to see if they
  affect the expected results.
* Errors in red; SamSifter will attempt to abort the processing immediately if
  it encounters an error.

Stopping a Workflow
-------------------
If you notice that you made a mistake or that the processing doesn't work as
expected you can abort the run by pressing the **[Stop]** button at any time.
Depending on your workflow this may leave temporary files in your work directory
that should be removed manually to not affect the next run.

.. _save_workflows:

Loading and Saving Workflows
============================

SamSifter uses a simple XML file type with the extension ``ssx`` (SamSifter XML) 
that is human- and machine-readable can be opened and edited in any text editor.

Use the **[Open]** button or the corresponding entry **[File] > [Open]** in the 
menu to open a workflow file located on your computer or network.

To save your workflow to a SSX file you can click the **[Save]** button in the
toolbar or choose the corresponding entry **[File] > [Save]** in the menu.
Similarly, use **[File] > [Save as...]** to save a copy of your current workflow
to a new file with different filename.

The **[File]** menu lists up to 10 recently used files for quicker access.

.. _bash_export:

Export to Bash scripts
======================

If processing one SAM file at a time is not enough anymore and you want to move
to large-scale processing of many files with an established workflow, maybe even
on bigger hardware with more CPU cores and RAM, then exporting your workflow
to a Bash script may be the next step.

All tools and filters included in SamSifter can also be executed as stand-alone
scripts on the commandline interface (CLI). To create a Bash script that can
call these commands similar to the graphical user interface (the SamSifter GUI)
simply click the **[Export]** button or select it from the
**[Run] > [Export to Bash]** menu. A dialog with several options will pop up,
allowing you to choose between three distinct types of processing modes and
giving you three addtional settings for Bash options (eg. to print all executed
commands, to shorten long file paths to just the filename and/or to stop on
errors):

.. image:: _images/bash_dialog.png
	:scale: 100%
	:alt: The Bash Export dialog offering three processing modes and three
	      additional settings.
	:align: center
	:target: _images/bash_dialog.png

The available processing modes are:

1. **Single Mode** processes only the specified input file and produces the
   specified output file similar to running the workflow in the GUI. This
   mode should be used with unmodified filenames unless all input files are
   located in the same directory as the exported bash script.

2. **Sequential Mode** processes a list of arbitrary input files one file
   after another and saves the output to files renamed with the filename
   extension ``sifted``. This mode should be used with shortened filenames
   unless all of the required list files (CSV) are available at identical
   paths from all machines that this script is deployed to.

3. **Parallel Mode** speeds up the process significantly by distributing jobs
   across all available CPU cores and running them in parallel. This requires
   the installation of GNU `parallel`. Similar to sequential mode above it
   should be used with shortened filenames unless all of the required list
   files (CSV) are available at identical paths from all machines that this
   script is deployed to.
   
Clicking the **[Save]** button lets you choose the name and location of the new
Bash script. Of course you can open this script in any text editor and modify it
to fit your needs. To execute the script you need to make it executable first::

	chmod +x example.sh
	
then run it with the command ::

	./example.sh one.sam two.sam three.sam
	
to process three different input files with the same example workflow. The number 
of input files is unlimited and they can be located anywhere on your computer or 
the network. The usual Bash wildcards like ``*`` and ``~`` can be used::

	./example.sh ~/test_dir/*.sam

would process all SAM files located in a directory called `test_dir` in the
user's home directory. If you 
have chosen the option to shorten filepaths to filenames only you need to keep 
any additional files like taxon lists or other CSVs in the same directory as the 
Bash script.

Running a Bash script that uses GNU `parallel` will show a summary of currently
running jobs, the number of available CPU cores, the average time per job as
well as an update on the estimated time until completion of all jobs (only 
available once the first jobs have finished).

.. _filter_manuals:

Manuals for Filters and Tools
=============================

.. _common_options:

Common Options
--------------
SamSifter includes a suite of built-in filters as well as wrappers for external
tools which are characterized by the name of the underlying tool in square 
brackets (eg. [SAMtools] or [PMDtools]). All of the built-in filters and also
some of the wrappers share a set of general options:

* **filter direction** has two possible settings: one *keeps* all entries in the
  analyzed file that match the filter requirements, the other *discards* these
  entries. By default all filters use the discard setting, but in case of eg.
  a pathogen screening with a small list of interesting taxon IDs it may be
  useful to invert this in order to *keep* all reads that map to a pathogen of
  interest.
* **verbose** is activated by default and provides additional information on the
  filter process. It can be safely deactivated, resulting in less noise in the
  messages dock and shorter log files on the command-line interface.
* **debug** is deactivated by default and prints information to the command-line
  which may help with troubleshooting and debugging the program. It is only
  useful to software developers.

.. Individual manuals for filters and tools are included here to increase
   modularity. References should be defined outside of the included documents
   to prevent duplication.

.. built-in analyzers
.. _count_taxon_reads:
.. include:: tools/count_taxon_reads.rst
.. built-in filters
.. _filter_read_conservation:
.. include:: tools/filter_read_conservation.rst
.. _filter_read_list:
.. include:: tools/filter_read_list.rst
.. _filter_ref_coverage:
.. include:: tools/filter_ref_coverage.rst
.. _filter_ref_identity:
.. include:: tools/filter_ref_identity.rst
.. _filter_ref_list:
.. include:: tools/filter_ref_list.rst
.. _filter_ref_pmds:
.. include:: tools/filter_ref_pmds.rst
.. _filter_taxon_list:
.. include:: tools/filter_taxon_list.rst
.. _filter_taxon_pmds:
.. include:: tools/filter_taxon_pmds.rst
.. GNU gzip wrappers
.. _compress:
.. include:: tools/compress.rst
.. _decompress:
.. include:: tools/decompress.rst
.. PMDtools wrappers
.. _calculate_pmds:
.. include:: tools/calculate_pmds.rst
.. _filter_read_identity:
.. include:: tools/filter_read_identity.rst
.. _filter_read_pmds:
.. include:: tools/filter_read_pmds.rst
.. SAMtools wrappers
.. _bam_2_sam:
.. include:: tools/bam_2_sam.rst
.. _sam_2_bam:
.. include:: tools/sam_2_bam.rst
.. _remove_duplicates:
.. include:: tools/remove_duplicates.rst
.. _sort_by_coordinates:
.. include:: tools/sort_by_coordinates.rst
.. _sort_by_names:
.. include:: tools/sort_by_names.rst
.. Wrappers for Paleogenetics Tools
.. _better_remove_duplicates:
.. include:: tools/better_remove_duplicates.rst

.. _statistics:

Statistical Summaries
=====================
Summaries of read counts before or after any step in a workflow can easily be
created by including one or more analysis steps (eg. :ref:`count_taxon_reads`)
in the workflow.

Compiling Results Per Analysed File
-----------------------------------
Each of these steps will create a temporary CSV file that is
removed once the data have been automatically compiled into a spreadsheet at the
end of a workflow. The tool responsible for this compilation is called
``compile_stats``. By default it is included in the post-processing of every
SamSifter workflow. It produces one CSV file for each
analysed SAM file with tab-separated columns: the first column contains the
taxon IDs, the following columns the read counts - one for each analysis step
that was included in the workflow. If no temporary files are found it does
nothing.

The statistics can be used to validate filter settings or their order and
evaluate the impact on size and composition of the filtered SAM file. One
example: If you are in doubt which threshold for a filter setting is going to
give the expected result you can create a cascade of filter steps, each with
slightly stricter thresholds than the previous and each followed by an analysis
step. By running the workflow once and looking at the resulting spreadsheet you
can then pinpoint the one filter threshold at which only the required entries
are left in the file. Your final workflow will then contain only one filter step
with this exact threshold and may even leave out the analysis step to save time.

Comparison of Multiple Files
----------------------------
When you repeat a workflow with different SAM files or use a Bash script to
process an entire batch of them (see :ref:`bash_export`), you can use the tool
``summarize_stats`` to combine all those individual statistics spreadsheets into
one summary file. All Bash scripts exported from SamSifter workflows that
provide batch processing functionalities already execute this tool by default.
The resulting spreadsheet will again contain taxon IDs in the first
column and then a bunch of columns with the final read counts for each analysed
SAM file. It can be very useful to quickly screen larger collections for 
interesting data and compare the results between individual files.

Enriching Summaries with External Databases
-------------------------------------------
Often a cryptic taxon ID is not sufficient to identify interesting entries in a
filtered SAM file. One example is additional information like species names in
English and Latin, host organisms or associated diseases that may be useful for
a filter workflow that screens metagenomic samples for human pathogens.

The tool ``enrich_summary`` combines SamSifter's statistical summaries with
any CSV file or database dump containing this additional
information. It is included in SamSifter, but is **not executed by default** as
the required data and settings will differ from use case to use case.

One potential source for such a database dump is the
`IMG/M database <https://img.jgi.doe.gov/cgi-bin/m/main.cgi?section=FindGenomes&page=genomeSearch>`_,
but in
theory all text dumps from arbitrary databases are supported. ``enrich_summary``
expects the database dump in a tab-delimited CSV format with
column headers. By default it searches for a column named `NCBI_ID` and
assumes that this column contains NCBI taxon IDs that match to those used in
the first column of the SamSifter summary file. Of course this index column can
be changed with a command-line option: ``--index my_taxon_id`` will look for a
column called `my_taxon_id` instead. By default the tool sorts the new, enriched
spreadsheet using a column called `Genome_Name`, but this sort field can also
be modified using the ``--sort my_species_name`` command-line option to sort by
`my_species_name` instead. The advantage of sorting by species name is the
clustering of taxonomically related entries in consecutive spreadsheet rows,
making interesting taxa, families or genera a lot easier to detect by visual
inspection.

A complete example related to the aforementioned screen of metagenomic samples
for human pathogens is the following command::

	enrich_summary --input samsifter.summary.csv --database imgm_database.txt --index 'NCBI Taxon ID' --sort 'Species' > samsifter.summary.enriched.csv
	
Here the ``--input`` SamSifter summary file is enriched with data from the
``--database`` IMG/M using the ``--index`` column called `NCBI taxon ID` and
sorted by ``--sort`` column `Species`. The results are written to a new CSV file.
If you have any doubts
about the spelling or meaning of any of these options you can always use the
built-in help function by calling this tool (and any of the other tools included
with SamSifter) with the option ``-h`` or ``--help`` to show the help text with
useful explanations.

.. seealso:: https://img.jgi.doe.gov/cgi-bin/m/main.cgi for the IMG/M database
             on Integrated Microbial Genomes with Microbiome Samples, which
             provides rich but uncurated annotations for microbial sequencing
             data. The integrated Genome Search functionality allows 
             downloads of customized database exports.
