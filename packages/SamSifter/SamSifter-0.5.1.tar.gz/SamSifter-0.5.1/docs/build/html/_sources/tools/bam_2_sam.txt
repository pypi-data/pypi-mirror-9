[SAMtools] Convert BAM to SAM
-----------------------------

This is a simple wrapper for SAMtools `view` which converts the binary BAM
format to the text-based SAM format by running the command ::

	samtools view -

The option to also print the SAM header (`-h` on the command-line interface) is 
enabled by default, as the information in those header lines is crucial for most
of SamSifter's filters.

.. seealso:: http://samtools.sourceforge.net/samtools.shtml
