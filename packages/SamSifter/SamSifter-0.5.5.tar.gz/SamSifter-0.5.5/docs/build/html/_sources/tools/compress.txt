[GNU gzip] Compress file
------------------------
This wrapper for GNU `gzip` compresses any uncompressed file. It should be
used only once towards the end of a workflow as frequent compression and
decompression between steps can slow processing down.

This step will simply execute the command ::
	
	gzip -c
	
and has no additional options.
