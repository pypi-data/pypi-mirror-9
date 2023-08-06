Filter references by % identity
-------------------------------
This is a two-step filter that first determines the number of reads mapping to a
reference with at least 90% identity, then identifies those references with at
least 50% reads passing the first threshold. Both filter settings can be changed
individually and the thresholds can also be set as upper instead of lower
limits. By default all references fulfilling the filter criteria are discarded.

.. note:: The % identity calculation is based on information in the CIGAR
          string and the optional MD tag and will fail if the SAM file contains
          no header.
