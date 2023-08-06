[SAMtools] Remove duplicates
----------------------------
This wrapper for SAMtools `rmdup` removes duplicate reads with identical start
coordinates from BAM files by running the command ::

	samtools rmdup - -

By default single-end reads are included in
duplicate removal. Paired-end reads can optionally be treated as single-end
reads.

.. seealso:: http://samtools.sourceforge.net/samtools.shtml

.. seealso:: :ref:`better_remove_duplicates` for the improved capabilities of
             Alexander Peltzer's `BetterRMDup` tool