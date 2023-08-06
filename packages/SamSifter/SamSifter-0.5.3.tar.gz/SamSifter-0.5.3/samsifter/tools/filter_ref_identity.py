#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Filters references by identity values of assigned reads.

This filter processes reference accessions with too few or too many reads of
high or low percent identity in MALT'ed SAM files.

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
from samsifter.util.arg_sanitation import (check_pos_float_max100, check_sam)
from samsifter.util.sam import reconstruct
from samsifter.util.genetics import aln_identity
from samsifter.util.filters import line_filter
from samsifter.util.papertrail import modify_header
from samsifter.version import samsifter_version

__version__ = samsifter_version

""" global variables """
TEXT = "Filter references by % identity"
DESC = ("Filters reference accessions with too few/many reads of high/low "
        "percent identity in MALT'ed SAM files")


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
        text="min. reads",
        desc="minimum percentage of reads with insufficient identity [50.0]",
        cli_name="--min_reads",
        default=50.0,
        unit="%",
        required=True,
        active=True
    ))

    item.add_parameter(FilterThreshold(
        text="max. reads",
        desc="maximum percentage of reads with insufficient identity [100.0]",
        cli_name="--max_reads",
        default=100.0,
        unit="%"
    ))

    item.add_parameter(FilterThreshold(
        text="min. identity",
        desc="minimum percent identity [90.0]",
        cli_name="--min_identity",
        default=90.0,
        unit="%",
        required=True,
        active=True
    ))

    item.add_parameter(FilterThreshold(
        text="max. identity",
        desc="maximum percent identity [100.0]",
        cli_name="--max_identity",
        default=100.0,
        unit="%"
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
    """Executable to filter SAM files for references with low identity reads.

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

    # thresholds for filtering
    threshold_options = parser.add_argument_group(
        title="filtering thresholds",
        description="modify cutoffs for percent identity filtering"
    )
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
    parser.add_argument('-m', '--modify',
                        required=False,
                        action='store_true',
                        help='modify header by adding PG record')

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
    header = []      # SAM header lines, unmodified
    filtered_counts = {}    # dict of list of ints: [passed, failed]
    positions = {}   # dict of list for references and their line numbers
    buffer = None    # file handle used to buffer complete STDIN
    byte_offset = 0  # offset of first line after end of header
    line_offset = 0

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

                accession = ""
                try:
                    accession = rname_parts[3]
                except IndexError:
                    accession = "unknown"
                    log.warn("no accession in line %s, assigning read to "
                             "accession 'unknown'" % (line_nr + 1))

                cigar = fields[5]
                read = fields[9]

                try:
                    md = line.split('MD:Z:')[1].split()[0].rstrip('\n')
                except IndexError:
                    log.error("no MD tag in line %s" % (line_nr + 1))
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

                # remember occurence of accession and line number(s)
                try:
                    positions[accession].append(line_nr)
                except KeyError:
                    positions[accession] = [line_nr, ]
    finally:
        handle.close()
        buffer.seek(0)

    # filter accessions by read thresholds
    log.info("STEP 2: determining accessions with "
             "%.1f%% <= filtered reads <= %.1f%%"
             % (args.min_reads, args.max_reads))
    lines = []
    for accession, (passed, failed) in filtered_counts.items():
        fraction = failed / (failed + passed)
        if args.debug:
            print(failed, passed, failed + passed, fraction, file=sys.stderr)
        if ((args.min_reads <= fraction * 100.0)
           and (fraction * 100.0 <= args.max_reads)):
            lines.extend(positions[accession])
            if args.debug:
                log.info("filtering accession: %s" % (accession,))

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

    log.info("END of filtering reads by identity.")

    exit()

if __name__ == "__main__":
    main()
