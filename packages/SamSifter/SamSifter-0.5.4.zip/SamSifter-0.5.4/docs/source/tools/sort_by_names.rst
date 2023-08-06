[SAMtools] Sort by query names
------------------------------
This wrapper for SAMtools `sort` sorts entries in a BAM file by their
query names (unique read identifiers) by running the command ::

	samtools sort -n - tmp -o

and has no additional options. Sorting uses a temporary file with prefix ``tmp``
that will briefly occupy additional storage space in the current work directory
if the whole alignment does not fit into memory.

.. seealso:: http://samtools.sourceforge.net/samtools.shtml
