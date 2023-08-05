#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filter references with high attribution of ancient reads in a MALT'ed and
PMD'ed SAM file

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
from samsifter.util.arg_sanitation import (check_pos_int, check_sam,
                                           check_percent)
from samsifter.util.wrappers import grep

""" global variables """
TEXT = "Filter references by PMD score"
DESC = ("Filter taxa with high attribution of ancient reads in a MALT'ed and "
        "PMD'ed SAM file")


def item():
    """
    Create FilterItem for this filter to be used in list and tree models.
    """
    item = FilterItem(text=TEXT, desc=DESC)

    min_pmd_param = FilterThreshold("min. PMDS",
                                    "minimum post-mortem degradation "
                                    "score (PMDS)",
                                    "--pmds",
                                    unit=None,
                                    required=True,
                                    active=True)
    min_pmd_param.setMinimum(-10)
    min_pmd_param.setMaximum(10)
    min_pmd_param.setDefault(3)
    min_pmd_param.setPrecision(0)
    min_pmd_param.setRequired(True)
    item.addParameter(min_pmd_param)

    min_read_param = FilterThreshold("min. reads",
                                     "minimum percentage of reads "
                                     "exceeding PMD threshold [50.0]",
                                     "--reads_perc",
                                     unit="%",
                                     required=True,
                                     active=True)
    min_read_param.default = 50.0
    min_read_param.setRequired(True)
    item.addParameter(min_read_param)

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
                        action='store_true',
                        help='print additional information to stderr')
    parser.add_argument('-p', '--pmds',
#                        dest='pmds',
                        required=True,
                        type=float,
                        help='post-mortem degradation score (PMDS) threshold')
    read_thresholds = parser.add_mutually_exclusive_group(required=True)
    read_thresholds.add_argument('-rp', '--reads_perc',
#                                 dest='reads_perc',
                                 type=check_percent,
                                 help='attributed read threshold (percent)')
    read_thresholds.add_argument('-rt', '--reads_total',
#                                 dest='reads_total',
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
    buffer = None   # file handle used to buffer complete STDIN

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

        for line_nr, line in enumerate(handle, 1):
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
                accession = ""
                try:
                    accession = rname_parts[3]
                except IndexError:
                    accession = "unspecified reference"
                    log.warn("no accession in line %i, run MALT version "
                             "0.0.3 or higher" % (line_nr, ))

                # extract PMD score from optional NS field
                # (written by pmdtools)
                pmds = 0
                try:
                    ns_parts = fields[18].split(":")
                    pmds = float(ns_parts[2])
                except ValueError:
                    log.error("invalid PMD score in line %i: %s"
                              % (line_nr, ns_parts[2]))
                    exit(1)
                except IndexError:
                    log.error("no PMD score in line %i, run 'pmdtools --dry "
                              "--header --writesamfield' first" % (line_nr, ))
                    exit(1)

                # count and filter reads by PMDS
                if (accession in totalReadCounts):
                    totalReadCounts[accession] += 1
                else:
                    totalReadCounts[accession] = 1

                if (pmds >= args.pmds):
                    if (accession in ancientReadCounts):
                        ancientReadCounts[accession] += 1
                    else:
                        ancientReadCounts[accession] = 1
    finally:
        handle.close()
        buffer.seek(0)

    # filter references
    log.info("STEP 2: determining references matching the filter criteria.")
    patterns = []
    for (accession, ancientReadCount) in sorted(ancientReadCounts.items()):
        if args.reads_total:
            if (ancientReadCount >= args.reads_total):
                patterns.append(accession)
#                log.info("filtering accession: %s" % (accession, ))
#                print(accession, file=sys.stdout)
        elif args.reads_perc:
            perc = ancientReadCount / totalReadCounts[accession] * 100.0
            if (perc >= args.reads_perc):
                patterns.append(accession)
#                log.info("filtering accession: %s" % (accession, ))
#                print(accession, file=sys.stdout)

    # keep or remove accessions from SAM file
    alt = ["discarding", "keeping"]
    log.info("STEP 3: %s %i references from SAM file." %
             (alt[args.discard], len(patterns)))
    if buffer is None:
        buffer = open(args.input, 'r')
    grep(patterns, buffer, discard=(args.discard == 0))
    buffer.close()

    log.info("END of filtering references by PMDS.")

    exit()

if __name__ == "__main__":
    main()
