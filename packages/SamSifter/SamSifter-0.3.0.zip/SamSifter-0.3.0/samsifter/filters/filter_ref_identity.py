#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filters reference accessions with too few/many reads of high/low percent
identity in MALT'ed SAM files"

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
from samsifter.util.arg_sanitation import (check_pos_float_max100, check_sam)
from samsifter.util.sam import reconstruct
from samsifter.util.genetics import aln_identity
from samsifter.util.wrappers import grep


""" global variables """
TEXT = "Filter references by % identity"
DESC = ("Filters reference accessions with too few/many reads of high/low "
        "percent identity in MALT'ed SAM files")


def item():
    """
    Create FilterItem for this filter to be used in list and tree models.
    """
    item = FilterItem(text=TEXT, desc=DESC)

    min_read_param = FilterThreshold("min. reads",
                                     "minimum percentage of reads with "
                                     "insufficient identity [50.0]",
                                     "--min_reads",
                                     unit="%",
                                     required=True,
                                     active=True)
    min_read_param.default = 50.0
    item.addParameter(min_read_param)

    max_read_param = FilterThreshold("max. reads",
                                     "maximum percentage of reads with "
                                     "insufficient identity [100.0]",
                                     "--max_reads",
                                     unit="%",
                                     required=False,
                                     active=False)
    max_read_param.default = 100.0
    item.addParameter(max_read_param)

    min_id_param = FilterThreshold("min. identity",
                                   "minimum percent identity [90.0]",
                                   "--min_identity",
                                   unit="%",
                                   required=True,
                                   active=True)
    min_id_param.default = 90.0
    item.addParameter(min_id_param)

    max_id_param = FilterThreshold("max. identity",
                                   "maximum percent identity [100.0]",
                                   "--max_identity",
                                   unit="%",
                                   required=False,
                                   active=False)
    max_id_param.default = 100.0
    item.addParameter(max_id_param)

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

    # thresholds for filtering
    threshold_options = parser.add_argument_group(
        title="filtering thresholds",
        description="modify cutoffs for percent identity filtering")
    threshold_options.add_argument("--min_reads",
                                   action="store",
                                   type=check_pos_float_max100,
                                   dest="min_reads",
                                   help="minimum percentage of reads with \
                                   insufficient identity [50.0]",
                                   default=50.0)
    threshold_options.add_argument("--max_reads",
                                   action="store",
                                   type=check_pos_float_max100,
                                   dest="max_reads",
                                   help="maximum percentage of reads with \
                                   insufficient identity [100.0]",
                                   default=100.0)
    threshold_options.add_argument("--min_identity",
                                   action="store",
                                   type=check_pos_float_max100,
                                   dest="min_identity",
                                   help="minimum percent identity [90.0]",
                                   default=90.0)
    threshold_options.add_argument("--max_identity",
                                   action="store",
                                   type=check_pos_float_max100,
                                   dest="max_identity",
                                   help="maximum percent identity [100.0]",
                                   default=100.0)

    # options to modify calculation of percent identity
    perc_id_options = parser.add_argument_group(
        title="percent identity",
        description=("Options to modify calculation of percent identity. "
                     "Setting all three options will calculate values similar "
                     "to PMDtools, while the default settings calculate "
                     "values similar to MALT."))
    perc_id_options.add_argument("--no_deamination",
                                 action="store_true",
                                 dest="no_deamination",
                                 help="do not treat possibly deaminated T>C \
                                 and A>G pairs as mismatches in calculation \
                                 of percent identity",
                                 default=False)
    perc_id_options.add_argument("--no_indels",
                                 action="store_true",
                                 dest="no_indels",
                                 help="do not treat insertions and deletions \
                                 in alignment as mismatches in calculation of \
                                 percent identity",
                                 default=False)
    perc_id_options.add_argument("--no_unknown",
                                 action="store_true",
                                 dest="no_unknown",
                                 help="do not treat Ns in alignment as \
                                 mismatch in calculation of percent identity",
                                 default=False)

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

    (args, remainArgs) = parser.parse_known_args()

    # configure logging
    if args.verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

    # exclude senseless threshold combinations
    if ((args.min_reads >= args.max_reads)
       or (args.min_identity >= args.max_identity)):
        log.error("Filter thresholds too restrictive.")
        exit(1)

    # initialize dicts and variables
    filtered_counts = {}    # dict of list of ints: [passed, failed]
    buffer = None   # file handle used to buffer complete STDIN

    log.info("START of filtering references by identity.")

    # parse SAM file and filter reads by identity thresholds
    log.info("STEP 1: parsing SAM records and determining reads with"
             " %.1f%% <= identity <= %.1f%%"
             % (args.min_identity, args.max_identity))
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

#                taxonId = ""
#                try:
#                    taxonId = rname_parts[5]
#                except IndexError:
#                    taxonId = "unspecified taxon"
#                    log.warn("no taxon ID in line %s, run MALT version \
#                             0.0.3 or higher" % (line_nr,))

                accession = ""
                try:
                    accession = rname_parts[3]
                except IndexError:
                    accession = "unspecified accession"
                    log.warn("no accession in line %s, run MALT version \
                             0.0.3 or higher" % (line_nr,))

                cigar = fields[5]
                read = fields[9]

                try:
                    md = line.split('MD:Z:')[1].split()[0].rstrip('\n')
                except IndexError:
                    log.error("no MD tag in line %s" % (line_nr, ))
                    exit(1)

                # recreate alignment
                (ref_full, read_full, ref_aln, read_aln) = reconstruct(read,
                                                                       cigar,
                                                                       md,
                                                                       False)

                # calculate identity of alignment
                # (PMD method, uses inverted defaults)
                include_indels = not args.no_indels
                include_deamination = not args.no_deamination
                include_unknown = not args.no_unknown
                (identity, mm_string) = aln_identity(read_aln,
                                                     ref_aln,
                                                     include_indels,
                                                     include_deamination,
                                                     include_unknown)

                # filter alignment, count results
                if ((args.min_identity <= identity * 100)
                   and (identity * 100 <= args.max_identity)):
                    # passed
                    try:
                        filtered_counts[accession][0] += 1
                    except KeyError:
                        filtered_counts[accession] = [1, 0]
                else:
                    # failed
                    try:
                        filtered_counts[accession][1] += 1
                    except KeyError:
                        filtered_counts[accession] = [0, 1]
    finally:
        handle.close()
        buffer.seek(0)

    # filter accessions by read thresholds
    log.info("STEP 2: determining accessions with "
             "%.1f%% <= filtered reads <= %.1f%%"
             % (args.min_reads, args.max_reads))
    patterns = []
    for accession, (passed, failed) in filtered_counts.items():
        fraction = failed / (failed + passed)
        if args.debug:
            print(failed, passed, failed + passed, fraction, file=sys.stderr)
        if ((args.min_reads <= fraction * 100.0)
           and (fraction * 100.0 <= args.max_reads)):
            patterns.append(accession)
#            log.info("filtering accession: %s" % (accession,))
#            print(accession, file=sys.stdout)

    # keep or remove accessions from SAM file
    alt = ["discarding", "keeping"]
    log.info("STEP 3: %s %i references from SAM file." %
             (alt[args.discard], len(patterns)))
    if buffer is None:
        buffer = open(args.input, 'r')
    grep(patterns, buffer, discard=(args.discard == 0))
    buffer.close()

    log.info("END of filtering reads by identity.")

    exit()

if __name__ == "__main__":
    main()
