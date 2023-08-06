#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Filters highly conserved reads in a SAM file.

Identifies reads assigned to multiple taxa with similar identity. Excludes
reads mapping to different accessions/taxa with similar alignment scores.

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
from samsifter.util.arg_sanitation import (check_sam, check_pos_int)
from samsifter.util.filters import line_filter
from samsifter.util.papertrail import modify_header
from samsifter.version import samsifter_version

__version__ = samsifter_version

""" global variables """
TEXT = "Filter reads by conservation"
DESC = ("Filters reads assigned to multiple taxa with similar identity. "
        "Excludes reads mapping to different accessions/taxa with similar "
        "alignment scores.")


def item():
    """Create FilterItem for this filter to be used in list and tree models.

    Returns
    -------
    FilterItem
        Object representing this filter in item-based models.
    """
    item = FilterItem(text=TEXT, desc=DESC)
    item.set_command(splitext(basename(__file__))[0])

    item.add_parameter(FilterThreshold(
        text="AS deviation",
        desc="permitted deviation from max alignment score [5]",
        cli_name="--as_dev",
        default=5,
        minimum=1,
        precision=0,
        required=True
    ))

    item.add_parameter(FilterThreshold(
        text="max. taxa",
        desc="maximum number of taxa [10]",
        cli_name="--max_taxa",
        default=10,
        minimum=1,
        precision=0,
        required=True
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
    """Executable to filter SAM files for reads with high conservation.

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
                        required=False,
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
    parser.add_argument("--as_dev",
                        action="store",
                        type=check_pos_int,
                        dest="as_dev",
                        help=("permitted deviation from max alignment score "
                              "[5]"),
                        default=5)
    parser.add_argument("--max_taxa",
                        action="store",
                        type=check_pos_int,
                        dest="max_taxa",
                        help="maximum number of taxa [10]",
                        default=10)

    (args, remainArgs) = parser.parse_known_args()

    # configure logging
    if args.verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

    # initialize dicts and variables
    header = []      # SAM header lines, unmodified
    queries = {}     # dict of dicts of lists: query -> score -> taxa
    positions = {}   # dict of list for QNAMES and their line numbers
    buffer = None    # file handle used to buffer complete STDIN
    byte_offset = 0  # offset of first line after end of header
    line_offset = 0

    log.info("START of filtering reads by conservation.")

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

            # assuming that headers always precede alignments (SAMv1)
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
                #   content     description
                ===========================
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
                11  AS          alignment score
                12  NM          edit distance to reference
                13  ZL          reference length
                14  ZR          "raw score"
                15  ZE          "expected"
                16  ZI          percent identify (incl. indels & deaminated)
                17  MD          mismatching positions
                18  NS          PMD score
                """

                if len(fields) < 10:
                    continue

                # extract accession from required RNAME field
                # (as written by MALT 0.0.3)
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

                try:
                    taxon_id = rname_parts[5]
                except IndexError:
                    taxon_id = "unknown"
                    log.warn("no taxon ID in line %i, assigning read to taxon "
                             "'unknown'" % (line_nr + 1))

                try:
                    aln_score = int(
                        line.split('AS:i:')[1].split()[0].rstrip('\n')
                    )
                except IndexError:
                    log.error("no AS tag in line %i" % (line_nr + 1))
                    exit(1)

                qname = fields[0]
                if qname in queries:
                    try:
                        # new taxon entry
                        queries[qname][aln_score].append(taxon_id)
                    except KeyError:
                        # new score entry
                        queries[qname][aln_score] = [taxon_id, ]
                else:
                    # new query entry
                    queries[qname] = {aln_score: [taxon_id, ]}

                # remember occurence of qname and line number(s)
                try:
                    positions[qname].append(int(line_nr))
                except KeyError:
                    positions[qname] = [int(line_nr), ]

    finally:
        handle.close()
        buffer.seek(0)

    # determine query names w/ high-scoring hits in several taxa
    log.info("STEP 2: determining query names matching the filter criteria.")
    lines = []
    for queryname in queries:
        score_dict = queries[queryname]

        # upper and lower bound
        max_score = max(score_dict.keys())
        if args.debug:
            log.info(
                "max_score: %s of type %s\targs.as_dev: %s of type %s"
                % (max_score, type(max_score), args.as_dev, type(args.as_dev))
            )
        low_bound = max_score - args.as_dev
        if low_bound < 0:
            low_bound = 0

        # compile list of taxa from the top
        taxon_list = []
        for score in range(low_bound, max_score + 1):
            try:
                taxon_list += score_dict[score]
            except KeyError:
                # some scores in range may be missing
                pass

        if len(set(taxon_list)) > args.max_taxa:
            lines.extend(positions[queryname])
            if args.debug:
                log.info("filtering query name: %s" % queryname)

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

    # keep or remove query names from SAM file
    alt = ["discarding", "keeping"]
    log.info("STEP 3: %s %i conserved reads from SAM file." %
             (alt[args.discard], len(lines)))

    line_filter(lines, buffer, discard=(args.discard == 0),
                offset=line_offset)
    buffer.close()

    log.info("END of filtering reads by conservation.")

    exit()

if __name__ == "__main__":
    main()
