.. _help:

==============
SamSifter Help
==============

.. .. contents:: Contents

Manual
======

.. toctree::
    :maxdepth: 4

    manual

Frequently Asked Questions
==========================

None so far...

Known Bugs
==========

Please report new bugs to f.aldehoff@student.uni-tuebingen.de.

Bugs in SamSifter
-----------------

* The 'Export to Bash' dialog fails to save the file when SamSifter has been
  started from the GNOME/KDE/Unity menu. Saving SSX files works fine, however.
  Workaround: Save Workflow to SSX, close SamSifter, open SamSifter from Shell
  and retry exporting the Bash script.

Bugs in Tools used by SamSifter
-------------------------------

* BetterRMDup fails when processing MALT'ed files. This is actually a bug of
  the SAM parsing library used in BetterRMDup that does not handle the custom MALT
  ``@mm`` record properly. The bug has been reported and will be fixed in a future
  version.
* SAMtools ``view`` reports a possibly truncated file and complains about a
  missing EOF marker. This is likely a bug in either
  MALT and/or SAMtools ``view`` which can be safely ignored. See
  http://sourceforge.net/p/samtools/mailman/samtools-help/thread/4EC52844.3090808@broadinstitute.org/
  for details. It is caused by a missing compression flag when processing
  uncompressed files.
* SAMtools ``view`` complains about inconsistency of the sequence length when
  compared to the CIGAR string. This is a bug in MALT 0.0.12 that has been
  reported. Please re-MALT your files with a newer version or remove the
  affected reads manually.
