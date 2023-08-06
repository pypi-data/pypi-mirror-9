[GNU gzip] Decompress file
--------------------------
A wrapper for GNU `gzip` that decompresses any zipped file. It should be used
only once towards the start of a workflow as frequent compression and
decompression between steps can slow processing down.

This step simply runs the command ::

	gzip -d
	
and has no additional options.
