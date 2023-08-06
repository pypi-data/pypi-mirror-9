Filter taxa by list of taxon IDs
--------------------------------
This filter is used to remove specific taxa from a SAM file by using a list of
unique NCBI taxon IDs. The list should be formatted as tab-separated CSV file and
list the taxon IDs in the first column without headers. Any additional columns
will be ignored. By default all reads mapping to a taxon in the list will
be discarded.
