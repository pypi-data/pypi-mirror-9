Filter reads by list of QNAMES
------------------------------
This filter is used to remove specific reads from a SAM file by using a list of
unique read identifiers (so-called QNAMES or query names). The list should be
formatted as tab-separated CSV file and list the query names in the first
column without headers. Any additional columns will be ignored.
