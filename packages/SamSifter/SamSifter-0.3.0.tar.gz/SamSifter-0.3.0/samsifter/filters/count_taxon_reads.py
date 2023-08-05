#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Analysing filter step to measure read counts per taxon.

@author: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

import sys
if not (sys.version_info[0] >= 3):
    print("Error, I need python 3.x or newer")
    exit(1)

import argparse
import logging as log
import fileinput
from os.path import basename, splitext, isfile

""" custom libraries """
from samsifter.models.filter import FilterItem
from samsifter.models.parameter import FilterParameter, FilterFilepath
from samsifter.util.arg_sanitation import check_sam

""" global variables """
TEXT = "Count reads per taxon"
DESC = ("Counts reads per taxon ID and stores them in a separate statistics "
        "file.")


def item():
    """
    Create FilterItem for this filter to be used in list and tree models.
    """
    item = FilterItem(text=TEXT, desc=DESC, icon=FilterItem.ICON_ANALYZER)

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

    p_prefix = FilterFilepath("prefix",
                              "prefix of temporary statistics files",
                              "--prefix",
                              required=False,
                              active=True)
    p_prefix.setDefault('${filename}')      # crucial for clean batch processing!
    item.addParameter(p_prefix)

    item.setEditable(False)

    # input/output requirements
    item.set_input_format('SAM')
    item.set_input_sorting('any')
    item.set_input_compression('uncompressed')
    item.set_output_format('SAM')
    item.set_output_sorting('as_input')
    item.set_output_compression('uncompressed')

    item.setCommand(splitext(basename(__file__))[0])  # entry point
#    item.setCommand(basename(__file__))               # filename only
#    item.setCommand(__file__)                         # full path
    return item


def main():
    # parse arguments
    parser = argparse.ArgumentParser(description=DESC)
    parser.add_argument('-i', '--input',
                        type=check_sam,
                        help="specify SAM file to be analysed (default: "
                        "STDIN)",
                        required=False)
    parser.add_argument('-p', '--prefix',
                        required=False,
                        default='reads_per_taxon',
                        help='prefix of temporary statistics files')
    parser.add_argument('-v', '--verbose',
                        required=False,
                        action='store_true',
                        help='print additional information to STDERR')
    parser.add_argument('-d', '--debug',
                        required=False,
                        action='store_true',
                        help='print debug messages to STDERR')
    (args, remainArgs) = parser.parse_known_args()

    # configure logging
    if args.verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

    log.info("START of counting reads per taxon.")

    # initialize dict
    counts = {}

    # parse SAM file
    log.info("STEP 1: parsing SAM records.")
    try:
        # open SAM file from either command line argument or STDIN
        if args.input:
            handle = open(args.input, 'r')
        else:
            handle = fileinput.input(remainArgs)

        for line_nr, line in enumerate(handle, 1):
            if not line.startswith("@"):
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

                # extract taxon ID from required RNAME field
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
                    taxon_id = 'unknown'
                    log.warn("no taxon ID in line %s, assigning read to "
                             "taxon 'unknown'" % (line_nr,))

                # add to counts
                try:
                    counts[taxon_id] += 1
                except KeyError:
                    counts[taxon_id] = 1

            print(line.rstrip(), file=sys.stdout)

    finally:
        handle.close()

    # check if previous statistic files exist and choose filename accordingly
    suffix = 'csv'
    # assuming that 999 filter steps will suffice
    for idx in range(1, 1000):
        stats_filename = '%s.%03d.%s' % (args.prefix, idx, suffix)
        if not isfile(stats_filename):
            break

    log.info("STEP 2: writing statistics to %s." % stats_filename)
    with open(stats_filename, mode='w') as handle:
        print("'taxon_id','read_count'", file=handle)
        for k, v in sorted(counts.items()):
            print("'%s',%i" % (k, v), file=handle)

    log.info("END of counting reads per taxon.")

    exit()

if __name__ == "__main__":
    main()
