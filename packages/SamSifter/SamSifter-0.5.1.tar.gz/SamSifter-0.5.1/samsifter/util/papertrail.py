#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Annotation of SAM file headers with metadata on applied programs.

.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""
import sys
import fileinput


def find_last_in_chain(current_id, pg_entries):
    """Recursively identify the last program entry in the chain.

    @PG entries in SAM file headers can be chained by linking each entry to the
    previously applied program using the optional PP tag. The actual last entry
    of the chain can only be found under the assumption that all programs are
    listed within one chain.

    Note
    ----
    May lead to wrong assumptions about the actual order of programs applied to
    dataset if the chain of PG entries is interrupted by missing PP tags. Use
    at own risk!

    Parameters
    ----------
    current_id : str
        Unique ID of program entry that serves as arbitrary start point for the
        recursive search of the chain end.
    pg_entries : dict of dicts
        Dictionary of @PG record tags (key:value) referenced by their unique
        program ID.

    Returns
    -------
    str
        Unique ID of the assumed last entry in the program chain (see note
        above!)
    """
    for entry, tags in pg_entries.items():
        try:
            if current_id == tags['PP']:
                # another entry follows
                return find_last_in_chain(entry, pg_entries)
        except KeyError:
            # entry has no PP tag
            continue
    # no other entry follows
    return current_id


def modify_header(lines, name=None, command_line=None, description=None,
                  version=None):
    """Modify SAM header by inserting a new @PG record into the chain.

    Ensures unique program identifiers and integrity of program chain.
    New entries are always inserted after all current PG entries and their
    order is not changed in case the entries are not chained by optional PP
    tags.

    Note
    ----
    Chaining of entries with PP tags is disabled as the chain of programs is
    often incomplete and may be misleading! The recursion through existing
    entries may not always be sufficient to identify the current last entry in
    the chain.

    Parameters
    ----------
    lines : list of str
        Full set of header lines of SAM file, including the first header line
        with @HD record.
    name : str, optional
        Program name, defaults to None.
    command_line : str, optional
        Program command line excluding program name/call, just the optional and
        positional arguments. Defaults to None.
    description : str, optional
        Short description of program functionality.
    version : str, optional
        Program version number/string.
    """
    hd = None           # first header line, required if header present
    pg = []             # list of PG header lines
    pg_entries = {}     # dict of dict for program records and their tags
    others = []         # list of other header lines

    # parse old header
    for line in lines:
        if line.startswith('@HD'):
            hd = line
        elif line.startswith('@PG'):
            pg.append(line)
            fields = line.lstrip('@PG\t').split('\t')
            tags = {}
            identifier = None
            for field in fields:
                (key, value) = field.rstrip().split(':')
                if key == 'ID':
                    identifier = value
                tags[key] = value

            # store program entry
            pg_entries[identifier] = tags
        else:
            others.append(line)

    # disabled as chain is often incomplete and may be misleading!
#    # recursively identify last program in chain, start with arbitrary entry
#    current_id = next(iter(pg_entries.keys()))
#    last = find_last_in_chain(current_id, pg_entries)

    # generate unique but short and consecutive identifier for new @PG record
    new_id = str(name)
    suffix = 0
    while new_id in pg_entries.keys():
        suffix += 1
        new_id = "%s_%i" % (name, suffix)

    # create new @PG line
    new_pg = create_pg_line(new_id,
                            name=name,
                            command_line=command_line,
                            # deactivated chaining, see above
                            # previous=last,
                            previous=None,
                            description=description,
                            version=version)

    # insert new PG line into the rest of the lines
    modified = [hd]
    modified.extend(pg)
    modified.append(new_pg)
    modified.extend(others)

    return modified


def create_pg_line(identifier, name=None, command_line=None, previous=None,
                   description=None, version=None):
    """Create a @PG header for SAM files.

    Follows SAMv1 specification, see
    https://samtools.github.io/hts-specs/SAMv1.pdf

    Parameters
    ----------
    identifier : str
        Unique program identifier within the context of the current SAM file
        that is identical to the identifier used in the alignment section. May
        be modified by later processing steps.
    name : str, optional
        Program name, defaults to None.
    command_line : str, optional
        Program command line excluding program name/call, just the optional and
        positional arguments. Defaults to None.
    previous : str, optional
        Program identifier of previous step in program chain.
    description : str, optional
        Short description of program functionality.
    version : str, optional
        Program version number/string.

    Returns
    -------
    str
        Complete standard-compliant @PG header line.
    """

    line = '@PG'

    # Program record identifier. Each @PG line must have a unique ID. The value
    # of ID is used in the alignment PG tag and PP tags of other @PG lines. PG
    # IDs may be modified when merging SAM files in order to handle collisions.
    pg_id = 'ID:%s' % identifier
    line += '\t' + pg_id

    # Program name, optional
    if name is not None:
        pg_pn = 'PN:%s' % name
        line += '\t' + pg_pn

    # Command line, optional
    if command_line is not None:
        pg_cl = 'CL:%s' % command_line
        line += '\t' + pg_cl

    # Previous @PG-ID. Must match another @PG header’s ID tag. @PG records may
    # be chained using PP tag, with the last record in the chain having no PP
    # tag. This chain defines the order of programs that have been applied to
    # the alignment. PP values may be modified when merging SAM files in order
    # to handle collisions of PG IDs. The first PG record in a chain (i.e. the
    # one referred to by the PG tag in a SAM record) describes the most recent
    # program that operated on the SAM record. The next PG record in the chain
    # describes the next most recent program that operated on the SAM record.
    # The PG ID on a SAM record is not required to refer to the newest PG
    # record in a chain. It may refer to any PG record in a chain, implying
    # that the SAM record has been operated on by the program in that PG
    # record, and the program(s) referred to via the PP tag.
    if previous is not None:
        pg_pp = 'PP:%s' % previous
        line += '\t' + pg_pp

    # Description, optional
    if description is not None:
        pg_ds = 'DS:%s' % description
        line += '\t' + pg_ds

    # Program version, optional
    if version is not None:
        pg_vn = 'VN:%s' % version
        line += '\t' + pg_vn

    line += '\n'

    return line


def main():
    """Simple test of PG header generation."""
    handle = fileinput.input(sys.argv)
    header = []
    for line_nr, line in enumerate(handle):
        if line.startswith('@'):
            header.append(line)
    handle.close()

    modified = modify_header(header, name='Test')
    for line in modified:
        print(line.rstrip(), file=sys.stdout)

if __name__ == "__main__":
    main()
