[PMDtools] Filter reads by PMDS
-------------------------------
This filter uses a modified version of PMDtools to calculate the post-mortem
degradation score (PMDS) for each read and discards all reads with scores below
the set threshold.

PMDtools can only calculate post-mortem degradation scores
for SAM files which contain a complete header with CIGAR strings and optional MD
tags because it has to reconstruct the reference sequence from these fields.
The tool can optionally write a brief statistical summary to the Messages dock
when done, however this is disabled by default.

.. seealso:: `Skoglund et al. (2014) <http://www.pnas.org/content/111/6/2229.abstract>`_
             for details on the calculation of post-mortem degradation scores
             and the original version of PMDtools.
