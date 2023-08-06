Filter references by list of accessions
---------------------------------------
This filter is used to remove specific reads from a SAM file by using a list of
unique accessions. The list should be formatted as tab-separated CSV file and
list the accessions in the first column without headers. Any additional columns
will be ignored. By default all reads mapping to an accession in the list will
be discarded.
