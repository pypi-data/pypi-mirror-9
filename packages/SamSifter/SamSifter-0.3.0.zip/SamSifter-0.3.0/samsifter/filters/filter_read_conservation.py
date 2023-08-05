#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Identify highly conserved reads in a SAM file.

Excludes reads mapping to different accessions/taxa with similar
alignment scores.

@author: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
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
from samsifter.util.arg_sanitation import (check_sam, check_pos_int)
from samsifter.util.wrappers import grep

""" global variables """
TEXT = "Filter reads by conservation"
DESC = ("Filters reads assigned to multiple taxa with similar identity. "
        "Excludes reads mapping to different accessions/taxa with similar "
        "alignment scores.")


def item():
    """
    Create FilterItem for this filter to be used in list and tree models.
    """
    item = FilterItem(text=TEXT, desc=DESC)

    t_as_dev = FilterThreshold("AS deviation",
                               "permitted deviation from max alignment score "
                               "[5]",
                               "--as_dev",
                               None)
    t_as_dev.setMinimum(1)
    t_as_dev.setDefault(5)
    t_as_dev.setPrecision(0)
    t_as_dev.setRequired(True)
    item.addParameter(t_as_dev)

    t_max_taxa = FilterThreshold("max. taxa",
                                 "maximum number of taxa [1]",
                                 "--max_taxa",
                                 None)
    t_max_taxa.setMinimum(1)
    t_max_taxa.setDefault(10)
    t_max_taxa.setMaximum(100)
    t_max_taxa.setPrecision(0)
    t_max_taxa.setRequired(True)
    item.addParameter(t_max_taxa)

    p_discard = FilterSwitch("filter direction",
                             "Keep or discard entries passing the filter "
                             "criteria?",
                             "--discard",
                             options=["discard", "keep"],
                             required=False,
                             active=False)
    p_discard.setDefault(0)
    item.addParameter(p_discard)

    p_verbose = FilterParameter("verbose",
                                "print additional information to STDERR",
                                "--verbose",
                                required=False,
                                active=True)
    p_verbose.setDefault(True)
    item.addParameter(p_verbose)

    p_debug = FilterParameter("debug",
                              "print debug messages to STDERR",
                              "--debug",
                              required=False,
                              active=False)
    p_debug.setDefault(False)
    item.addParameter(p_debug)

    item.setEditable(False)
    item.setCommand(splitext(basename(__file__))[0])  # entry point
#    item.setCommand(basename(__file__))               # filename only
#    item.setCommand(__file__)                         # full path
    return item


def main():
    # parse arguments
    parser = argparse.ArgumentParser(description=DESC)
#    parser.add_argument("sam",
#                        type=check_sam,
#                        help="SAM file to be analysed")
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
                        help="maximum number of taxa [1]",
                        default=1)

    (args, remainArgs) = parser.parse_known_args()

    # configure logging
    if args.verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

    # initialize dicts and variables
    header = []    # SAM header lines, unmodified
#    prev_qname = ""
    queries = {}    # dict of dicts of lists: query -> score -> taxa
    buffer = None   # file handle used to buffer complete STDIN

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

        for line_nr, line in enumerate(handle, 1):
            if buffer is not None:
                buffer.write(line)

            if line.startswith("@"):
                header.append(line)
                # TODO modify header lines for program history
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
                    taxon_id = "unspecified taxon"
                    log.warn("no taxon ID in line %s, run MALT version 0.0.3 "
                             "or higher" % (line_nr,))

#                try:
#                    accession = rname_parts[3]
#                except IndexError:
#                    accession = "unspecified accession"
#                    log.warn("no accession in line %s, run MALT version 0.0.3 "
#                             "or higher" % (line_nr,))

                try:
                    aln_score = int(line.split('AS:i:')[1].split()[0].rstrip('\n'))
                except IndexError:
                    log.error("no AS tag in line %s" % (line_nr,))
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

#                prev_qname = qname

    finally:
        handle.close()
        buffer.seek(0)

    # determine query names w/ high-scoring hits in several taxa
    log.info("STEP 2: determining query names matching the filter criteria.")
    patterns = []
    for queryname in queries:
        score_dict = queries[queryname]

        # upper and lower bound
        max_score = max(score_dict.keys())
#        log.info("max_score: %s of type %s\targs.as_dev: %s of type %s" %
#                 (max_score, type(max_score),
#                  args.as_dev, type(args.as_dev)))
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
            patterns.append(queryname)
#            log.info("filtering query name: %s" % (queryname,))
#            print(queryname, file=sys.stdout)

    # keep or remove query names from SAM file
    alt = ["discarding", "keeping"]
    log.info("STEP 3: %s %i conserved reads from SAM file." %
             (alt[args.discard], len(patterns)))
    if buffer is None:
        buffer = open(args.input, 'r')
    grep(patterns, buffer, discard=(args.discard == 0))
    buffer.close()

    log.info("END of filtering reads by conservation.")

    exit()

if __name__ == "__main__":
    main()
