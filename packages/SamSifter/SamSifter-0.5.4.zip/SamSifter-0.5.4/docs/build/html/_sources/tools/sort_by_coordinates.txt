[SAMtools] Sort by coordinates
------------------------------
This wrapper for SAMtools `sort` sorts entries in a BAM file by their
coordinates by running the command ::

	samtools sort - tmp -o

and has no additional options. Sorting uses a temporary file with prefix ``tmp``
that will briefly occupy additional storage space in the current work directory
if the whole alignment does not fit into memory.

.. seealso:: http://samtools.sourceforge.net/samtools.shtml
