#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filter taxa with high attribution of ancient reads in a MALT'ed and PMD'ed
SAM file

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
from samsifter.models.parameter import (FilterParameter, FilterSwitch,
                                        FilterThreshold)
from samsifter.util.arg_sanitation import (check_pos_int, check_sam,
                                           check_percent)
from samsifter.util.filters import line_filter

""" global variables """
TEXT = "Filter taxa by PMD score"
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

    return item


def main():
    """Executable to filter SAM files for taxa with ancient reads.

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

    totalReadCounts = {}
    ancientReadCounts = {}
    header = []
    positions = {}   # dict of list for taxon IDs and their line numbers
    buffer = None    # file handle used to buffer complete STDIN

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
                header.append(line)
                # TODO modify header lines for program history
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
                taxonId = ""
                try:
                    taxonId = rname_parts[5]
                except IndexError:
                    taxonId = "unspecified taxon"
                    log.warn("no taxon ID in line %i, run MALT version 0.0.3 "
                             "or higher" % (line_nr + 1))

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
                        "--header --writesamfield' first" % (line_nr + 1)
                    )
                    exit(1)

                # count and filter reads by PMDS
                if (taxonId in totalReadCounts):
                    totalReadCounts[taxonId] += 1
                else:
                    totalReadCounts[taxonId] = 1

                if (pmds >= args.pmds):
                    if (taxonId in ancientReadCounts):
                        ancientReadCounts[taxonId] += 1
                    else:
                        ancientReadCounts[taxonId] = 1

                # remember occurence of taxon ID and line number(s)
                try:
                    positions[taxonId].append(line_nr)
                except KeyError:
                    positions[taxonId] = [line_nr, ]
    finally:
        handle.close()
        buffer.seek(0)

    # filter taxa
    log.info("STEP 2: determining taxa matching the filter criteria.")
    lines = []
    for (taxonId, ancientReadCount) in sorted(ancientReadCounts.items()):
        if args.reads_total:
            if (ancientReadCount >= args.reads_total):
                lines.extend(positions[taxonId])
                if args.debug:
                    log.info("filtering taxon: %s" % taxonId)
        elif args.reads_perc:
            perc = ancientReadCount / totalReadCounts[taxonId] * 100.0
            if (perc >= args.reads_perc):
                lines.extend(positions[taxonId])
                if args.debug:
                    log.info("filtering taxon: %s" % taxonId)

    # keep or remove taxa from SAM file
    alt = ["discarding", "keeping"]
    log.info("STEP 3: %s %i taxa from SAM file." %
             (alt[args.discard], len(lines)))
    if buffer is None:
        buffer = open(args.input, 'r')
    line_filter(lines, buffer, discard=(args.discard == 0))
    buffer.close()

    log.info("END of filtering taxa by PMDS.")

    exit()

if __name__ == "__main__":
    main()
