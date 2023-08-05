#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Identify reference accessions with uneven coverage in MALT'ed SAM files.

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
import re
import matplotlib as mpl
mpl.use('Agg')       # before importing numpy, else trouble on headless server
import matplotlib.pyplot as plt
import numpy as np

""" custom libraries """
from samsifter.models.filter import FilterItem
from samsifter.models.parameter import (FilterParameter, FilterSwitch,
                                        FilterThreshold, FilterFilepath)
from samsifter.util.arg_sanitation import (check_pos_float,
                                           check_pos_float_max1,
                                           check_pos_int, check_sam)
from samsifter.util.wrappers import grep

""" global variables """
TEXT = "Filter references by evenness of coverage"
DESC = ("Filters reference accessions exceeding a Gini Index threshold.")


def item():
    """
    Create FilterItem for this filter to be used in list and tree models.
    """
    item = FilterItem(text=TEXT, desc=DESC)

    p_min_gini = FilterThreshold("min. Gini",
                                 "minimum Gini coefficient",
                                 '--min_gini',
                                 required=False,
                                 active=False)
    p_min_gini.setMinimum(0.00)
    p_min_gini.setDefault(0.00)
    p_min_gini.setMaximum(1.00)
    p_min_gini.setPrecision(2)
    item.addParameter(p_min_gini)

    p_max_gini = FilterThreshold("max. Gini",
                                 "maximum Gini coefficient",
                                 '--max_gini',
                                 required=True,
                                 active=True)
    p_max_gini.setMinimum(0.00)
    p_max_gini.setDefault(1.00)
    p_max_gini.setMaximum(1.00)
    p_max_gini.setPrecision(2)
    item.addParameter(p_max_gini)

    p_read_lengths = FilterParameter("read lengths",
                                     "analyze read length distributions",
                                     "--read_lengths",
                                     required=False,
                                     active=False)
    p_read_lengths.setDefault(False)
    item.addParameter(p_read_lengths)

    p_covered = FilterParameter("covered bases only",
                                "covered bases only, ignore uncovered bases",
                                "--covered",
                                required=False,
                                active=False)
    p_covered.setDefault(False)
    item.addParameter(p_covered)

    p_stats_file = FilterFilepath("statistics file",
                                  "override filename for tab-separated "
                                  "statistics [${filename}.stats.csv]",
                                  '--stats_file',
                                  required=False,
                                  active=False)
    p_stats_file.setDefault("${filename}.stats.csv")
    item.addParameter(p_stats_file)

    p_plot = FilterParameter("plot distribution(s)",
                             "plot coverage and/or read length distributions",
                             "--plot",
                             required=False,
                             active=False)
    p_plot.setDefault(False)
    item.addParameter(p_plot)

    p_lci_arg = FilterThreshold("LCI argument",
                                "fraction of mean coverage to use for LCI "
                                "integration",
                                '--lci_arg',
                                required=False,
                                active=False)
    p_lci_arg.setMinimum(0.00)
    p_lci_arg.setDefault(0.50)
    p_lci_arg.setMaximum(1.00)
    p_lci_arg.setPrecision(2)
    item.addParameter(p_lci_arg)

    p_min_lci = FilterThreshold("min. LCI",
                                "minimum low-coverage index",
                                '--min_lci',
                                required=False,
                                active=False)
    p_min_lci.setMinimum(0.0)
    p_min_lci.setDefault(0.0)
    p_min_lci.setMaximum(1000.0)
    item.addParameter(p_min_lci)

    p_max_lci = FilterThreshold("max. LCI",
                                "maximum low coverage index",
                                '--max_lci',
                                required=False,
                                active=False)
    p_max_lci.setMinimum(0.0)
    p_max_lci.setDefault(1000.0)
    p_max_lci.setMaximum(1000.0)
    item.addParameter(p_max_lci)

    p_min_cov = FilterThreshold("min. coverage",
                                "minimum average coverage",
                                '--min_cov',
                                required=False,
                                active=False)
    p_min_cov.setMinimum(0)
    p_min_cov.setDefault(0)
    p_min_cov.setMaximum(9999)
    p_min_cov.setPrecision(0)
    item.addParameter(p_min_cov)

    p_max_cov = FilterThreshold("max. coverage",
                                "maximum average coverage",
                                '--max_cov',
                                required=False,
                                active=False)
    p_max_cov.setMinimum(0)
    p_max_cov.setDefault(9999)
    p_max_cov.setMaximum(9999)
    p_max_cov.setPrecision(0)
    item.addParameter(p_max_cov)

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


""" plotting methods """


def plot_rld(ax, length_dist, min_length, max_length, read_count,
             length_dist_total):
    """
    Create a bar plot of a read length distribution.

    Includes scaled expected distribution based on all reads in file.
    """
    ax.set_title('RLD')
    ax.bar(np.arange(length_dist.size),
           length_dist,
           align='center',
           width=0.8,
           color='gray',
           label='actual')
    ax.plot(np.arange(min_length, max_length + 1, dtype=np.int),
            # scale expected dist down
            (length_dist_total * 1.0 / read_count) * np.sum(length_dist),
            color='red',
            linestyle='dashed',
            label='expected')
    ax.axis([min_length, max_length, 0, None])
    ax.set_xlabel("read length [bp]")
    ax.set_ylabel("number of reads")


def plot_cd(ax, depth_dist, avg_depth):
    """
    Create a bar plot of a cumulative coverage distribution.
    """
    ax.set_title("CD")
    ax.bar(np.arange(depth_dist.size, dtype=np.int),
           depth_dist,
           align='center',
           width=0.8,
           color='gray')
    ax.axis([-0.5, depth_dist.size - 0.5, 0, None])
    ax.axvline(x=avg_depth,
               color='green',
               label="avg. coverage: %.2fx" % (avg_depth,))
    ax.set_xlabel("coverage")
    ax.set_ylabel("reference bases")
    ax.legend(loc=1)  # upper right


def plot_scd(ax, depth_dist, avg_depth, ref_length, max_depth):
    """
    Create a bar plot of a scaled cumulative coverage distribution.
    """
    depth_dist = depth_dist * 1.0 / ref_length

    ax.set_title("SCD")
    ax.bar(np.arange(depth_dist.size, dtype=np.int),
           depth_dist,
           align='center',
           width=0.8,
           color='gray')
    ax.axis([-0.5, depth_dist.size - 0.5, 0, 1])
    ax.axvline(x=avg_depth,
               color='green',
               label="avg. coverage: %.2fx" % (avg_depth,))
    ax.set_xlabel("coverage")
    ax.set_ylabel("fraction of reference bases")
    ax.legend(loc=1)  # upper right


def plot_ccd(ax, depth_dist_cumsum, avg_depth):
    """
    Create a bar plot of a cumulative coverage distribution.
    """
    ax.set_title("CCD")
    ax.bar(np.arange(depth_dist_cumsum.size, dtype=np.int),
           depth_dist_cumsum,
           align='center',
           width=0.8,
           color='gray')
    ax.axis([-0.5, depth_dist_cumsum.size - 0.5, 0, None])
#    ax.axis([None, None, 0, None])

    ax.axvline(x=avg_depth,
               color='green',
               label="avg. coverage: %.2fx" % (avg_depth,))
    ax.set_xlabel("coverage")
#    ax.set_xticks(None, None, 1.0)
    ax.set_ylabel("cumulative bases")


def plot_sccd(ax, depth_dist_cumperc, avg_depth):
    """
    Create a bar plot of a scaled cumulative coverage distribution.
    """
    ax.set_title("SCCD")
    ax.bar(np.arange(depth_dist_cumperc.size),
           depth_dist_cumperc,
           align='edge',
           width=1,
           color='gray')
    ax.axis([0, depth_dist_cumperc.size - 1, 0, None])
    ax.axvline(x=avg_depth,
               color='green',
               label="avg. coverage: %.2fx" % (avg_depth,))
    ax.set_xlabel("coverage")
    ax.set_ylabel("cumulative fraction of alignment")


def plot_nccd(ax, depth_dist_cumperc, avg_depth, max_depth, avg_depth_scaled,
              lci, color):
    """
    Create a bar plot of a normalized cumulative coverage distribution.

    Includes legend stating average scaled and total depth
    """
    ax.set_title("NCCD")
    ax.bar(np.arange(depth_dist_cumperc.size) * 1.0 / max_depth,
           depth_dist_cumperc,
           align='edge',
           width=1.0 / (depth_dist_cumperc.size - 1),
           color=color)
    ax.axis([0, 1, 0, 1])
    ax.axvline(x=avg_depth_scaled,
               color='green',
               label="avg. coverage: %.2f [%.2fx]" % (avg_depth_scaled,
                                                      avg_depth))
    ax.axvline(x=lci * avg_depth_scaled,
               linestyle='dashed',
               color='green',
               label="%.2f x avg. cov.: %.2f [%.2fx]" % (
                   lci, lci * avg_depth_scaled, lci * avg_depth))
    ax.set_xlabel("fraction of max coverage")
    ax.set_ylabel("cumulative fraction of alignment")
    ax.legend(loc=4)  # lower right


def plot_lorenz(ax, x, y):
    """
    Create a Lorenz curve plot of a coverage distribution.
    """
    (gini, auc) = get_gini_auc(x, y)

    ax.set_title("Lorenz")

    # show equal distribution
    ax.plot([0, 1],
            [0, 1],
#            linestyle='--',
            color='green',
            label="equal distribution")
#    ax.fill([0,1,1], [0,1,0], color='green', alpha=0.5)

    # show actual distribution
    ax.plot(x, y, label="actual distribution")
    ax.fill(x, y, color='gray', alpha=0.2)

    ax.axis([0, 1, 0, 1])

    ax.set_xlabel("fraction of coverage bins")
    ax.set_ylabel("fraction of alignment")
    ax.text(0.05, 0.75, "Gini = %.2f" % (gini,), transform=ax.transAxes)

    ax.legend(loc=2)  # upper left


def plot_lorenz_b2b(ax, x, y):
    """
    Create a Lorenz curve plot of a coverage distribution.
    """
    (gini, auc) = get_gini_auc(x, y)

    ax.set_title("Lorenz base2base")

    # show equal distribution
    ax.plot([0, 1],
            [0, 1],
#            linestyle='--',
            color='green',
            label="equal distribution")
#    ax.fill([0,1,1], [0,1,0], color='green', alpha=0.5)

    # show actual distribution
    ax.plot(x, y, label="actual distribution")
    ax.fill(x, y, color='gray', alpha=0.2)

    ax.axis([0, 1, 0, 1])

    ax.set_xlabel("fraction of reference bases")
    ax.set_ylabel("fraction of aligned read bases")
    ax.text(0.05, 0.75, "Gini = %.2f" % (gini,), transform=ax.transAxes)

    ax.legend(loc=2)  # upper left


""" Integration methods """


def integral_discrete(dist, limit):
    """
    Integrate discrete distribution with stepsize 1 by simply adding up values.
    """
    return np.sum(dist[0:limit]) / 100.0


def integral_scaled(dist, limit):
    """
    Integrate scaled discrete distribution with arbitrary stepsize.
    """
    area = 0

    # prevent division by zero (for cases with 100% 1x coverage)
    if dist.size == 1:
        return 1.0 * limit

    # scale limit by max depth
    if limit <= dist.size - 1:
        limit_scaled = limit * 1.0 / (dist.size - 1)
    else:
        limit_scaled = 1.0
#    print("limit\t%f" % (limit_scaled,))

    stepsize = 1.0 / (dist.size - 1)
    x = stepsize
    for y in np.nditer(dist):
        if limit_scaled > x:
            area += stepsize * y
#            print("area for x = %f\t%f" % (x, area))
        else:
            area += (limit_scaled - (x - stepsize)) * y
#            print("area for x = %f\t%f" % (limit_scaled, area))
            break
        x += stepsize

    return area


def lorenzify(depth_dist):
    """
    Calculate Lorenz curve from coverage distribution.
    """
    reads_sum = np.sum(depth_dist)
    dd_scaled = depth_dist * 1.0 / reads_sum
    dd_sorted = np.sort(dd_scaled)
    dd_cum = np.cumsum(dd_sorted)

    # append (0|0) origin to beginning of arrays
    y = np.append(np.array([0.0]), dd_cum)
    x = np.append(np.array([0.0]),
                  (np.arange(depth_dist.size) + 1) * 1.0 / depth_dist.size)

    return (x, y)


def lorenzify_b2b(depth_dist, ignore_uncovered=True):
    """
    Calculate Lorenz curve from base2base coverage distribution.
    """
#    start = time.time()

    ali_total = 0
    ref_total = 0

#    base2base_list = []
    ali_bases_list = []
    ref_bases_list = []
    for (coverage, count) in enumerate(depth_dist):
        if ignore_uncovered:
            if coverage == 0:
                continue
        ali_bases = count * coverage
        ali_bases_list.append(ali_bases)
        ref_bases_list.append(count)

        ali_total += ali_bases
        ref_total += count

#        base2base_list.append((aligned_bases, count))

    # turn lists into arrays and scale them
    b = np.array(ref_bases_list) * 1.0 / ref_total
    v = np.array(ali_bases_list) * 1.0 / ali_total

    triples = np.array([b, v, v/b])
    ttriples = np.transpose(triples)
#    triples.sort(axis = 0) # not working...
    tttriples = np.transpose(ttriples[ttriples[:, 2].argsort()])

#    sorted_pairs = sorted(base2base_list)
#    sorted_aligned_bases = []
#    sorted_ref_bases = []
#    for pair in sorted_pairs:
#        sorted_aligned_bases.append(pair[0])
#        sorted_ref_bases.append(pair[1])
#
#    x = np.cumsum(sorted_ref_bases)
#    y = np.cumsum(sorted_aligned_bases)

    x = np.cumsum(tttriples[0])
    y = np.cumsum(tttriples[1])

    # append (0|0) origin to beginning of arrays, scale both axes on the fly
    x = np.append(np.array([0]), x)   # * 1.0 / total_ref_bases
    y = np.append(np.array([0]), y)   # * 1.0 / total_aligned_bases

#    stop = time.time()
#    print("lorenzify_b2b took %f s for %i bp aligned to a %i bp reference"
#          % (stop - start, ali_total, ref_total))

    return (x, y)


def get_gini_auc(x, y):
    """
    Calculate Gini coefficient and area under Lorenz curve.

    Expects arrays of x and y coordinates for a normalized Lorenz distribution.
    """

    # calculate area under curve
    auc = 0.0
    for (idx, value) in enumerate(x):
        # no area at origin (0|0)
        if idx == 0:
            continue
        square = (x[idx] - x[idx - 1]) * y[idx - 1]
        triangle = ((x[idx] - x[idx - 1]) * (y[idx] - y[idx - 1])) / 2.0
        auc = auc + square + triangle

    # calculate Gini coefficient (area under normalized equal dist is 0.5)
#    gini = (0.5 - auc) / 0.5
    gini = 1.0 - (2 * auc)  # equivalent, but faster?

    return (gini, auc)


def covered_length_from_cigar(cigar):
    """
    Calculate length of reference covered by read from CIGAR operations.

    - not counting padding, skipping or insertions into the reference
    - not counting hard or soft clipped bases of the read
    """
    regex = re.compile("(\d+)([MIDNSHP=X])")
    length = 0
    for match in regex.finditer(cigar):
#        print(match.group(0), match.group(1), match.group(2))
        if match.group(2) in ("M", "=", "X", "D"):
            length += int(match.group(1))
    return length


def calc_avg_depth(depth_dist, ignore_uncovered=True):
    """
    Calculate average depth from a coverage distribution.

    Optionally ignores uncovered bases (first array element).
    """
    sum_bases = 0
    sum_cover = 0

    for (coverage, count) in enumerate(depth_dist):
        if ignore_uncovered:
            if coverage == 0:
                continue
        sum_bases += count
        sum_cover += coverage * count

    return sum_cover / (sum_bases * 1.0)


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
    parser.add_argument('-r', '--read_lengths',
                        required=False,
                        action='store_true',
                        help='analyze read length distributions')
    parser.add_argument('-c', '--covered',
                        required=False,
                        action='store_true',
                        help='covered bases only, ignore uncovered bases')
    parser.add_argument('-v', '--verbose',
                        required=False,
                        action='store_true',
                        help='print additional information to stderr')
    parser.add_argument('-d', '--debug',
                        required=False,
                        action='store_true',
                        help='print debug messages to stderr')
    parser.add_argument('--discard',
                        type=int,
                        help="keep or discard entries passing the filter "
                             "criteria?",
                        required=False,
                        default=0)
    parser.add_argument('-p', '--plot',
                        required=False,
                        action='store_true',
                        help='plot distribution(s)')
    parser.add_argument('-l', '--lci_arg',
                        required=False,
                        type=check_pos_float_max1,
                        help='fraction of mean coverage to use for LCI \
                        integration',
                        default=0.5)
    parser.add_argument('-s', '--stats_file',
                        required=False,
                        help="override filename for tab-separated statistics")

    acc_thresholds = parser.add_mutually_exclusive_group(required=False)
    acc_thresholds.add_argument('--min_cov',
                                type=check_pos_int,
                                help='minimum average coverage',
                                default=0)
    acc_thresholds.add_argument('--max_cov',
                                type=check_pos_int,
                                help='maximum average coverage',
                                default=sys.maxsize)
    acc_thresholds.add_argument('--min_lci',
                                type=check_pos_float,
                                help='minimum LCI',
                                default=0.0)
    acc_thresholds.add_argument('--max_lci',
                                type=check_pos_float,
                                help='maximum LCI',
                                default=1000.0)
    acc_thresholds.add_argument('--min_gini',
                                type=check_pos_float_max1,
                                help='minimum Gini coefficient',
                                default=0.0)
    acc_thresholds.add_argument('--max_gini',
                                type=check_pos_float_max1,
                                help='maximum Gini coefficient',
                                default=1.0)

    (args, remainArgs) = parser.parse_known_args()

    # configure logging
    if args.verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

#    if args.debug:
#        from pprint import pprint

    # set filename for statistics output
    if args.stats_file:
        stats_filename = args.stats_file
    elif args.input:
        stats_filename = args.input + ".stats.csv"
    else:
        # this assumes that filename was explicitly set by calling batch script
        # TODO check effect when run in normal pipe without specifying filename
        stats_filename = "${filename}.stats.csv"

    # initialize dicts
    depths = {}                     # dict of np.array of ints
    ref_lengths = {}                # dict of ints
    read_counts = {}                # dict of ints
    if args.read_lengths:
        read_lenghts = {}           # dict of dict of ints
        read_lenghtsTotal = {}      # dict of ints
    line_count = 0
    buffer = None   # file handle used to buffer complete STDIN

    # parse SAM file and divide reads by reference accession
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
            line_count = line_nr
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
                16  ZI          percent identify (incl. indels and deaminated)
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
#                    log.warn("no taxon ID in line %s" % (line_count, ),
#                             "run MALT version 0.0.3 or higher")

                accession = ""
                try:
                    accession = rname_parts[3]
                except IndexError:
                    accession = "unspecified accession"
                    log.warn("no accession in line %s" % (line_nr, ),
                             "run MALT version 0.0.3 or higher")

                # extract reference sequence length from optional ZL field
                ref_length = 0
                try:
                    zl_parts = fields[13].split(":")
                    ref_length = int(zl_parts[2])
                except IndexError:
                    log.error("no ZL field in line" % (line_nr, ))
                    exit(1)

                """
                read                ------------------------------
                ref     -----------------------------------------------------
                cover   00000000000011111111111111111111111111111100000000000
                            pre    |         covered              |   post
                                 start                           stop
                """

                # get 1-based start position of read from required POS field
                pre = int(fields[3]) - 1

                # obtain stop position from required CIGAR field
                covered = covered_length_from_cigar(fields[5])
                stop = pre + covered
                post = ref_length - covered - pre

#                # usage of Numpy arrays too slow and memory-consuming :-/
#                log.info("%s\t%i\t%i\t%i" % (accession, pre, covered, post))
#
#                coverage = np.concatenate((np.zeros((pre,), dtype=np.int),
#                                           np.ones((covered,), dtype=np.int),
#                                           np.zeros((post,), dtype=np.int)),
#                                          axis=0)
#
#                # add read to overall coverage of current accession
#                if accession in depths:
#                    depths[accession] = np.add(depths[accession], coverage)
#                else:
#                    depths[accession] = coverage

                if accession in depths:
                    read_counts[accession] += 1
                    for position in range(pre, stop + 1):
                        if position in depths[accession]:
                            depths[accession][position] += 1
                        else:
                            depths[accession][position] = 1
                else:
                    ref_lengths[accession] = ref_length
                    read_counts[accession] = 1
                    for position in range(pre, stop + 1):
                        depths[accession] = {position: 1}

                # optional: read length distribution
                if args.read_lengths:
                    readLen = len(fields[9])

                    if readLen in read_lenghtsTotal:
                        read_lenghtsTotal[readLen] += 1
                    else:
                        read_lenghtsTotal[readLen] = 1

                    if accession in read_lenghts:
                        if readLen in read_lenghts[accession]:
                            read_lenghts[accession][readLen] += 1
                        else:
                            read_lenghts[accession][readLen] = 1
                    else:
                        read_lenghts[accession] = {readLen: 1}
    finally:
        handle.close()
        buffer.seek(0)

    log.info("%i reads are aligned to %i references"
             % (line_count, len(depths)))

    # get overall read length statistics
    if args.read_lengths:
        max_length_total = max(read_lenghtsTotal.keys())
        min_length_total = min(read_lenghtsTotal.keys())
        length_dist_total = np.zeros(
            (max_length_total - min_length_total + 1, ), dtype=np.int)
        for (length, count) in read_lenghtsTotal.items():
            length_dist_total[length - min_length_total] = count

        log.info("read lengths range from %i to %i bp"
                 % (min_length_total, max_length_total))

    # iterate over accessions and calculate statistics for filtering
    log.info("STEP 2: determining accessions matching the filter criteria.")
    patterns = []
    max_depths = []
    max_lengths = []
    with open(stats_filename, "w") as handle:
        # create statistics header
        header = "accession\treference length [bp]\treads"
        if args.read_lengths:
            header += "\tmin length [bp]\tmax length [bp]\tmean length [bp]"
        header += "\tmin coverage\tmax coverage\tmean coverage"
        if args.covered:
            header += "\tmin coverage*\tmax coverage*\tmean coverage*"
        header += "\tLCI(%.2f)\tGini" % (args.lci_arg)
        if args.covered:
            header += "\tLCI(%.2f)*\tGini*" % (args.lci_arg)
        print(header, file=handle)

        for accession in depths:
            ref_length = ref_lengths[accession]
            read_count = read_counts[accession]

            # calculate coverage statistics
            max_depth = max(depths[accession].values())
            max_depths.append(max_depth)

            # determine depth distribution
            uncovered_bases = ref_length
            depth_dist = np.zeros((max_depth + 1,), dtype=np.int)
            for (pos, depth) in depths[accession].items():
                depth_dist[depth] += 1
                uncovered_bases -= 1
            depth_dist[0] = uncovered_bases
            if args.debug:
                print(depth_dist)

            min_depth = 0
            if uncovered_bases == 0:
                min_depth = min(depths[accession].values())
            avg_depth = calc_avg_depth(depth_dist, False)
            avg_depth_scaled = avg_depth * 1.0 / max_depth

            # convert counts to percentage of total reads (normalize y)
            depth_dist_cumsum = np.cumsum(depth_dist)
            depth_dist_cumperc = depth_dist_cumsum * 1.0 / (ref_length)

            # integrate distribution as lci(0.5)
            limit = args.lci_arg * avg_depth
#            lci = integral_discrete(depth_dist_cumperc, limit)
            lci = integral_scaled(depth_dist_cumperc, limit)

#            # calculate Gini coefficient from Lorenz curve
#            (x,y) = lorenzify(depth_dist)
#            (gini, auc) = get_gini_auc(x, y)

            # alternative Lorenz curve using base to base assignments
            (u, v) = lorenzify_b2b(depth_dist, False)
            if args.debug:
                print("x (%i entries): %s" % (len(u), u))
                print("y (%i entries): %s" % (len(v), v))
            (gini_b2b, auc_b2b) = get_gini_auc(u, v)

            # TODO calculate Theil index, see
            # https://en.wikipedia.org/wiki/Theil_Index

            # optional: coverage stats for covered bases only
            if args.covered:
                min_depth_covered = min(depths[accession].values())
                if uncovered_bases == 0:
                    min_depth_covered = min_depth
                avg_depth_covered = calc_avg_depth(depth_dist, True)
#                avg_depth_covered_scaled = avg_depth_covered * 1.0 / max_depth

                depth_dist_covered_cumsum = np.cumsum(depth_dist[1:])
                depth_dist_covered_cumperc = (depth_dist_covered_cumsum * 1.0
                                              / (ref_length - uncovered_bases))

                limit_covered = args.lci_arg * avg_depth_covered
                lci_covered = integral_scaled(depth_dist_covered_cumperc,
                                              limit_covered)

                (m, n) = lorenzify_b2b(depth_dist, True)
                if args.debug:
                    print("x (%i entries): %s" % (len(m), m))
                    print("y (%i entries): %s" % (len(n), n))
                (gini_b2b_covered, auc_b2b_covered) = get_gini_auc(m, n)

            # optional: read length stats
            if args.read_lengths:
                max_length = max(read_lenghts[accession].keys())
                min_length = min(read_lenghts[accession].keys())
                avg_length = np.mean(np.fromiter(
                    read_lenghts[accession].keys(), dtype=np.int,
                    count=len(read_lenghts[accession])))
                max_lengths.append(max_length)

                # determine length distribution
                length_dist = np.zeros((max_length + 1,), dtype=np.int)
                for (length, count) in read_lenghts[accession].items():
                    length_dist[length] = count

            # compile accession statistics
            stats = "%s\t%i\t%i" % (accession, ref_length, read_count)
            if args.read_lengths:
                stats += "\t%i\t%i\t%f" % (min_length, max_length, avg_length)
            stats += "\t%i\t%i\t%f" % (min_depth, max_depth, avg_depth)
            if args.covered:
                stats += "\t%i\t%i\t%f" % (min_depth_covered, max_depth,
                                           avg_depth_covered)
            stats += "\t%f\t%f" % (lci, gini_b2b)
            if args.covered:
                stats += "\t%f\t%f" % (lci_covered, gini_b2b_covered)
            print(stats, file=handle)

            # apply filters before time-consuming plotting steps
            if ((avg_depth < args.min_cov)
               or (avg_depth > args.max_cov)
               or (lci < args.min_lci)
               or (lci > args.max_lci)
               or (gini_b2b < args.min_gini)
               or (gini_b2b > args.max_gini)):
                continue

            color = 'blue'

            if args.plot:
                fig_cover = plt.figure(num=1,
                                       figsize=(24, 12),  # inch x inch
                                       dpi=80,            # 1 inch = 80 pixels
                                       facecolor='white',
                                       edgecolor='black')
#                x = np.arange(depth_dist_cumperc.size) * 1.0 / max_depth

                # CD = coverage distribution plot
                ax_cd = fig_cover.add_subplot(2, 4, 1)
                plot_cd(ax_cd, depth_dist, avg_depth)

                # SCD = scaled coverage distribution plot
                ax_scd = fig_cover.add_subplot(2, 4, 2)
                plot_scd(ax_scd, depth_dist, avg_depth, ref_length, max_depth)

                # SCD = scaled coverage distribution plot
                ax_scd_covered = fig_cover.add_subplot(2, 4, 3)
                plot_scd(ax_scd_covered,
                         np.append(np.array([0]), depth_dist[1:]),
                         avg_depth_covered,
                         ref_length - uncovered_bases,
                         max_depth)

#                # CCD = cumulative coverage distribution plot
#                ax_ccd = fig_cover.add_subplot(2, 4, 2)
#                plot_ccd(ax_ccd, depth_dist_cumsum, avg_depth)

#                # SCCD = scaled cumulative coverage distribution plot
#                ax_sccd = fig_cover.add_subplot(2, 4, 3)
#                plot_sccd(ax_sccd, depth_dist_cumperc, avg_depth)

                # NCCD = normalized cumulative coverage distribution
                ax_nccd = fig_cover.add_subplot(2, 4, 4)
                plot_nccd(ax_nccd, depth_dist_cumperc, avg_depth, max_depth,
                          avg_depth_scaled, args.lci_arg, color)
                ax_nccd.text(0.05, 0.95,
                             "lci(%.2f) = %.2f" % (args.lci_arg, lci),
                             transform=ax_nccd.transAxes)

#                # Lorenz curve
#                ax_lorenz = fig_cover.add_subplot(2, 4, 5)
#                plot_lorenz(ax_lorenz, x, y)

                # Lorenz curve base2base
                ax_b2b = fig_cover.add_subplot(2, 4, 6)
                plot_lorenz_b2b(ax_b2b, u, v)

                if args.covered:
                    ax_b2b_covered = fig_cover.add_subplot(2, 4, 7)
                    plot_lorenz_b2b(ax_b2b_covered, m, n)

                # save plot to png
                fig_cover.tight_layout()
                fig_cover.savefig(accession + "_coverage.png")
                plt.close(fig_cover)

                if args.read_lengths:
                    fig_readlength = plt.figure(num=2,
                                                figsize=(6, 6),  # inch x inch
                                                dpi=80,        # 1 inch = 80px
                                                facecolor='white',
                                                edgecolor='black')

                    # RLD = read length distribution
                    ax_rld = fig_readlength.add_subplot(1, 1, 1)
                    plot_rld(ax_rld, length_dist, min_length_total,
                             max_length_total, line_nr, length_dist_total)

                    # save plot to png
                    fig_readlength.savefig(accession + "_readlengths.png")
                    plt.close(fig_readlength)

            log.info("accession %s: reference has a length of %i bp and %i "
                     "aligned reads" % (accession, ref_length, read_count))
            log.info("accession %s: coverage ranges from %ix to %ix, average "
                     "is %.3fx" % (accession, min_depth, max_depth, avg_depth))
            if args.covered:
                log.info("accession %s: coverage for covered bases only "
                         "ranges from %ix to %ix, average is %.3fx"
                         % (accession, min_depth_covered, max_depth,
                            avg_depth_covered))
            if args.read_lengths:
                log.info("accession %s: read length ranges from %i bp to %i "
                         "bp, average is %.3f bp" % (accession, min_length,
                                                     max_length, avg_length))

            # finally print accession for later filtering steps
            patterns.append(accession)
            log.info("filtering accession: %s" % (accession,))
#            print(accession, file=sys.stdout)

    # keep or remove accessions from SAM file
    alt = ["discarding", "keeping"]
    log.info("STEP 3: %s %i unevenly covered references from SAM file." %
             (alt[args.discard], len(patterns)))
    if buffer is None:
        buffer = open(args.input, 'r')
    grep(patterns, buffer, discard=(args.discard == 0))
    buffer.close()

    log.info("END of filtering references by coverage, statistics saved to "
             "file %s" % (stats_filename, ))

    exit()


if __name__ == "__main__":
    main()
