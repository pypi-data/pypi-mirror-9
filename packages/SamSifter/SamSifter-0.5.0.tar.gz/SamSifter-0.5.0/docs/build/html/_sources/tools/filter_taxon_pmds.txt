Filter taxa by PMD score
------------------------
This is a two-step filter that calculates the post-mortem degradation score for
each read and in first step determines the number of ancient reads (PMDS at
least 3) mapping to a taxon, then identifies those taxa with at least
50% reads passing the first threshold. Both filter settings can be changed
individually. By default all references fulfilling the filter criteria are
discarded.

.. note:: The PMD score calculation is based on information in the CIGAR
          string and the optional MD tag and will fail if the SAM file contains
          no header.
