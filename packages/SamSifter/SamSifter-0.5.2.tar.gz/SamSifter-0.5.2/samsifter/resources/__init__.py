"""Resources for the SamSifter GUI.

Includes icons to be used for Qt4 widgets across all supported OS as well as
desktop files for menu entries according to the freedesktop.org standards.
XML-based Qt4 Resource files are compiled to binary Python resource objects
using the following command::

    pyrcc4 -py3 resources.qrc > resources.py

Note
----
The resulting module is *not* annotated or documented as recompilation will
overwrite all manual changes.


The resources file is simply imported (eg. in :py:mod:`samsifter.samsifter`) to
make the included icons available. Complaints about unused imports by code
checkers like *pyflake* can be safely avoided by asserting the import.
"""
