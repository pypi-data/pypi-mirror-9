Count reads per taxon
---------------------
This analysis step will not alter the input file but count the number of reads 
assigned to each taxon ID. The results are stored to a temporary statistics file
as comma-separated values (CSV) with taxon IDs in column `taxon_id` and the
read counts in column `read_count`.

Up to 1000 of these steps can be included in a workflow to compare read counts
between arbitrary filtering steps. The temporary files as well as the
corresponding read count columns will be enumerated from `000` to `999` and
compiled into one large spreadsheet during post-processing.

.. seealso:: :ref:`statistics`
