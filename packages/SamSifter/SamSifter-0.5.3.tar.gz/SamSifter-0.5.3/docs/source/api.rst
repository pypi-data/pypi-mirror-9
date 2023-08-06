.. _api:

===========================
SamSifter API documentation
===========================

SamSifter is written in Python3 and uses docstrings written in `reStructuredText 
(reST) format <http://docutils.sourceforge.net/rst.html>`_ following the `Numpy 
docstring standard 
<https://github.com/numpy/numpy/blob/master/doc/HOWTO_DOCUMENT.rst.txt#id4>`_
for the documentation of all classes and functions. The package is distributed 
through the `Python Package Inventory <https://pypi.python.org/pypi>`_ at 
https://pypi.python.org/pypi/SamSifter using functionality provided by Python's
:py:mod:`setuptools` library.

All entities follow the `PEP8 naming conventions 
<http://legacy.python.org/dev/peps/pep-0008/#naming-conventions>`_ using all 
lowercase names with underscores (``lower_case_with_underscores``) for packages, 
modules, methods, attributes, and functions but capitalized words (``CapWords``)
for classes *unless* they are referring to C++ methods that are part
of the PyQt4 library.

The following packages are included:

.. toctree::
   :maxdepth: 3

   pmdtools
   samsifter
