[SAMtools] Convert SAM to BAM
-----------------------------

This is a simple wrapper for SAMtools `view` which converts the text-based SAM
format to the binary BAM format by running the command ::

	samtools view -S -b -
	
The output is compressed by default but compression can be disabled to speed up
the following steps. This is only recommended when all following steps are part
of the SAMtools suite as well.

.. seealso:: http://samtools.sourceforge.net/samtools.shtml
