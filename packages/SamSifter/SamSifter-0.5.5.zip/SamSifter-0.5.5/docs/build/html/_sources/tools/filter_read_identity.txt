[PMDtools] Filter reads by % identity
-------------------------------------
This filter is a wrapper for a modified version of PMDtools that targets reads
with insufficient identity to their respective reference sequence. Any reads with
identity values below the set minimum threshold (default is 0.95 = 95%) will be
discarded.

.. note:: The calculation of identity according to PMDtools ignores indels,
          possibly deaminated bases as well as unknown bases (Ns). In order to
          achieve compatibility with MALT and other tools that include all of
          these in their calculation the three corresponding options have to be
          activated.

PMDtools can only calculate identity values for SAM files which
contain a complete header with CIGAR strings and optional MD tags because it
has to reconstruct the reference sequence from these fields. The tool can
optionally write a brief statistical summary to the Messages dock when done,
however this is disabled by default.

.. seealso:: `Skoglund et al. (2014) <http://www.pnas.org/content/111/6/2229.abstract>`_
             for the original version of PMDtools.
