"""Modules for general tasks shared among SamSifter, PMDtools and other tools.

Includes modules for the tasks of

* argument sanitation, eg. filetype, value type and range checks
* basic filter routines on file handles
* standard functions operating on nucleotide sequences
* annotation of SAM files with @PG records
* reconstruction of reference sequences from SAM records
* serialization of SamSifter workflows
* validation of SamSifter workflows

Some of these may be generalized and refactored into proper packages in future
releases.
"""
