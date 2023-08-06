[PMDtools] Calculate PMDS
-------------------------
This wrapper for a modified version of PMDtools does not have any filter
functionality but simply calculates the post-mortem degradation score for each
read and writes it into a custom DS tag by running the command ::

	pmdtools_mod --dry --writesamfield --header

Following PMDtools steps in the workflow will utilize these tags and skip the
calculation to save time.

PMDtools can only calculate post-mortem degradation scores for SAM files which
contain a complete header with CIGAR strings and optional MD tags because it
has to reconstruct the reference sequence from these fields. The tool can
optionally write a brief statistical summary to the Messages dock when done,
however this is disabled by default.

.. seealso:: `Skoglund et al. (2014) <http://www.pnas.org/content/111/6/2229.abstract>`_
             for details on the calculation of post-mortem degradation scores
             and the original version of PMDtools.
