#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filter references with high attribution of ancient reads in a MALT'ed and
PMD'ed SAM file

.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

import sys
if not (sys.version_info[0] >= 3):
    print("Error, I need python 3.x or newer")
    exit(1)

import argparse
import logging as log
import fileinput
import tempfile
from os.path import basename, splitext

""" custom libraries """
from samsifter.models.filter import FilterItem
from samsifter.models.parameter import (
    FilterParameter, FilterSwitch, FilterThreshold
)
from samsifter.util.arg_sanitation import (
    check_pos_int, check_sam, check_percent
)
from samsifter.util.filters import line_filter
from samsifter.util.papertrail import modify_header
from samsifter.version import samsifter_version

__version__ = samsifter_version

""" global variables """
TEXT = "Filter references by PMD score"
DESC = ("Filter taxa with high attribution of ancient reads in a MALT'ed and "
        "PMD'ed SAM file")


def item():
    """Create item representing this tool in list and tree views.

    Returns
    -------
    FilterItem
        Item for use in item-based list and tree views.
    """
    item = FilterItem(text=TEXT, desc=DESC)
    item.set_command(splitext(basename(__file__))[0])

    item.add_parameter(FilterThreshold(
        text="min. PMDS",
        desc="minimum post-mortem degradation score (PMDS)",
        cli_name="--pmds",
        default=3,
        minimum=-10,
        maximum=10,
        precision=0,
        required=True,
        active=True
    ))

    item.add_parameter(FilterThreshold(
        text="min. reads",
        desc="minimum percentage of reads exceeding PMD threshold [50.0]",
        cli_name="--reads_perc",
        default=50.0,
        unit="%",
        required=True,
        active=True
    ))

    item.add_parameter(FilterSwitch(
        text="filter direction",
        desc="Keep or discard entries passing the filter criteria?",
        cli_name="--discard",
        default=0,
        options=["discard", "keep"]
    ))

    item.add_parameter(FilterParameter(
        text="verbose",
        desc="print additional information to STDERR",
        cli_name="--verbose",
        default=True,
        active=True
    ))

    item.add_parameter(FilterParameter(
        text="debug",
        desc="print debug messages to STDERR",
        cli_name="--debug",
        default=False
    ))

    item.add_parameter(FilterParameter(
        text="write PG tag",
        desc="annotate the filtered SAM file by adding a PG tag to the header",
        cli_name="--modify",
        default=True,
        active=True
    ))

    return item


def main():
    """Executable to filter SAM files for references with ancient reads.

    See ``--help`` for details on expected arguments. Takes input from
    either STDIN, or optional, or positional arguments. Logs messages to
    STDERR and writes processed SAM files to STDOUT.
    """
    # parse arguments
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument('-i', '--input',
                        type=check_sam,
                        help="specify SAM file to be analysed (default: "
                        "STDIN)",
                        required=False)
    parser.add_argument('--discard',
                        type=int,
                        help="keep or discard entries passing the filter "
                             "criteria?",
                        required=False,
                        default=0)
    parser.add_argument('-v', '--verbose',
                        action='store_true',
                        help='print additional information to stderr')
    parser.add_argument('-d', '--debug',
                        required=False,
                        action='store_true',
                        help='print debug messages to stderr')
    parser.add_argument('-m', '--modify',
                        required=False,
                        action='store_true',
                        help='modify header by adding PG record')
    parser.add_argument('-p', '--pmds',
                        required=True,
                        type=float,
                        help='post-mortem degradation score (PMDS) threshold')
    read_thresholds = parser.add_mutually_exclusive_group(required=True)
    read_thresholds.add_argument('-rp', '--reads_perc',
                                 type=check_percent,
                                 help='attributed read threshold (percent)')
    read_thresholds.add_argument('-rt', '--reads_total',
                                 type=check_pos_int,
                                 help='attributed read threshold (total)')
    (args, remainArgs) = parser.parse_known_args()

    # configure logging
    if args.verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

    # initialize dicts and variables
    header = []      # SAM header lines, unmodified
    total_read_counts = {}
    ancient_read_counts = {}
    positions = {}   # dict of list for references and their line numbers
    buffer = None    # file handle used to buffer complete STDIN
    byte_offset = 0  # offset of first line after end of header
    line_offset = 0

    log.info("START of filtering references by PMDS.")

    # parse SAM file
    log.info("STEP 1: parsing SAM records.")
    try:
        """
        open SAM file from either command line argument or STDIN
        use temporary file as buffer if reading from STDIN
        """
        if args.input:
            handle = open(args.input, 'r')
        else:
            handle = fileinput.input(remainArgs)
            buffer = tempfile.TemporaryFile(mode='w+')

        for line_nr, line in enumerate(handle, 0):
            if buffer is not None:
                buffer.write(line)

            if line.startswith("@"):
                if args.modify:
                    line_offset = line_nr + 1
                    # store header lines for later modification
                    header.append(line)
                    # increase offset until reaching end of header
                    byte_offset += len(line)
            else:
                fields = line.split("\t")
                """
                #   content
                ====================
                0   QNAME
                1   FLAG
                2   RNAME
                3   POS
                4   MAPQ
                5   CIGAR
                6   RNEXT
                7   PNEXT
                8   TLEN
                9   SEQ
                10  QUAL
                ...optional fields...
                18  NS
                """

                # extract taxon ID from required RNAME field (written by MALT)
                rname_parts = fields[2].split("|")
                """
                #   content
                ===============
                0   gi
                1   GenBank ID
                2   ref
                3   accession
                4   tax
                5   taxonomy ID
                """
                accession = ""
                try:
                    accession = rname_parts[3]
                except IndexError:
                    accession = "unknown"
                    log.warn("no accession in line %s, assigning read to "
                             "accession 'unknown'" % (line_nr + 1))

                # extract PMD score from optional NS field
                # (written by pmdtools)
                pmds = 0
                try:
                    ns_parts = fields[18].split(":")
                    pmds = float(ns_parts[2])
                except ValueError:
                    log.error("invalid PMD score in line %i: %s"
                              % (line_nr + 1, ns_parts[2]))
                    exit(1)
                except IndexError:
                    log.error(
                        "no PMD score in line %i, run 'pmdtools --dry "
                        "--header --writesamfield' first" % (line_nr + 1))
                    exit(1)

                # count and filter reads by PMDS
                if (accession in total_read_counts):
                    total_read_counts[accession] += 1
                else:
                    total_read_counts[accession] = 1

                if (pmds >= args.pmds):
                    if (accession in ancient_read_counts):
                        ancient_read_counts[accession] += 1
                    else:
                        ancient_read_counts[accession] = 1

                # remember occurence of accession and line number(s)
                try:
                    positions[accession].append(line_nr)
                except KeyError:
                    positions[accession] = [line_nr, ]
    finally:
        handle.close()
        buffer.seek(0)

    # filter references
    log.info("STEP 2: determining references matching the filter criteria.")
    lines = []
    for (accession, ancientReadCount) in sorted(ancient_read_counts.items()):
        if args.reads_total:
            if (ancientReadCount >= args.reads_total):
                lines.extend(positions[accession])
                if args.debug:
                    log.info("filtering accession: %s" % (accession, ))
        elif args.reads_perc:
            perc = ancientReadCount / total_read_counts[accession] * 100.0
            if (perc >= args.reads_perc):
                lines.extend(positions[accession])
                if args.debug:
                    log.info("filtering accession: %s" % (accession, ))

    # re-open file if not a buffered stream
    if buffer is None:
        buffer = open(args.input, 'r')

    # skip original headers and sneak in modified headers instead
    if args.modify:
        log.info("Writing new @PG record to SAM header.")
        cl = " ".join(sys.argv[1:])
        modified_header = modify_header(
            header,
            name=splitext(basename(__file__))[0],
            version=__version__,
            command_line=cl,
            description=TEXT
        )
        extra_headers = len(modified_header) - len(header)    # should be 1
        for record in modified_header:
            print(record.rstrip(), file=sys.stdout)
        # fast forward buffer to beginning of alignments
        buffer.seek(byte_offset)

        if args.debug:
            log.info("%i new line added to header lines." % extra_headers)

    # keep or remove accessions from SAM file
    alt = ["discarding", "keeping"]
    log.info("STEP 3: %s %i references from SAM file." %
             (alt[args.discard], len(lines)))

    line_filter(lines, buffer, discard=(args.discard == 0),
                offset=line_offset)
    buffer.close()

    log.info("END of filtering references by PMDS.")

    exit()

if __name__ == "__main__":
    main()
