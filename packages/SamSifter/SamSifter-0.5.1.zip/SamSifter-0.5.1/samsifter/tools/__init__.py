"""Filters, tools and wrappers for the manipulation of SAM files.

This package includes a collection of stand-alone filters and tools as well as
wrappers for external tools that process SAM files in a POSIX pipeline context.
They can be divided into the following groups:

* **Analyzers** do not remove entries from the input file but may alter the
  contained information by adding additional tags. They can also create
  statistical summaries or plots based on features of the analyzed input.

* **Converters** do not remove entries but may change characteristics of the
  input file such as the file format, the sort order of the contained reads or
  the compression. They can be used to adapt the input file to requirements of
  the following steps in  analysis.

* **Filters** can remove entries from the input file based on different
  criteria. They may perform on any of the three levels read, reference and
  taxon (or a combination of these).

All modules in this package should provide an ``item()`` method which returns
an instance of :py:class:`samsifter.models.filter.FilterItem` representing the
tool and its parameters in the SamSifter GUI. This item should also point to
either the external command or the entry point of the script/tool/main method
that is supposed to be executed. The executable ``main()`` *may* be located
within the same module but this is not required at all.

New tools or wrappers need to be imported in :py:mod:`samsifter.samsifter` and
also registered in its method
:py:meth:`samsifter.samsifter.MainWindow.populate_filters`
to be selectable from the SamSifter main menu and tools dock. In case of Python
scripts it may be convenient to also add an entry point in :py:mod:`setup.py`
to let the Python installation routine automatically create executables that
work on any of the supported operating systems.
"""
