#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Identify reference accessions with uneven coverage in MALT'ed SAM files.

Comes with several methods to create optional plots of coverage and read length
distributions.

Warning
-------
Activating the plotting of these distributions for a large input dataset can
create I/O problems due to the large amounts of PNG files generated. It will
also decrease the performance of this filter considerably and should only be
used to troubleshoot filter parameters for small subsets of the data.

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
from samsifter.util.filters import line_filter
from samsifter.util.papertrail import modify_header
from samsifter.version import samsifter_version

__version__ = samsifter_version

""" global variables """
TEXT = "Filter references by evenness of coverage"
DESC = ("Filters reference accessions exceeding a Gini Index threshold.")


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
        text="min. Gini",
        desc="minimum Gini coefficient",
        cli_name='--min_gini',
        default=0.00,
        maximum=1.00
    ))

    item.add_parameter(FilterThreshold(
        text="max. Gini",
        desc="maximum Gini coefficient",
        cli_name='--max_gini',
        default=0.90,
        maximum=1.00,
        required=True,
        active=True
    ))

    item.add_parameter(FilterParameter(
        text="read lengths",
        desc="analyze read length distributions",
        cli_name="--read_lengths",
        default=False
    ))

    item.add_parameter(FilterParameter(
        text="covered bases only",
        desc="covered bases only, ignore uncovered bases",
        cli_name="--covered",
        default=False
    ))

    item.add_parameter(FilterFilepath(
        text="statistics file",
        desc=("override filename for tab-separated statistics "
              "[${filename}.stats.csv]"),
        cli_name='--stats_file',
        default="${filename}.stats.csv"
    ))

    item.add_parameter(FilterParameter(
        text="plot distribution(s)",
        desc="plot coverage and/or read length distributions",
        cli_name="--plot",
        default=False
    ))

#    item.add_parameter(FilterThreshold(
#        text="LCI argument",
#        desc="fraction of mean coverage to use for LCI integration",
#        cli_name='--lci_arg',
#        default=0.50,
#        maximum=1.00
#    ))
#
#    item.add_parameter(FilterThreshold(
#        text="min. LCI",
#        desc="minimum low-coverage index",
#        cli_name='--min_lci',
#        default=0.0,
#        maximum=1000.0
#    ))
#
#    item.add_parameter(FilterThreshold(
#        text="max. LCI",
#        desc="maximum low coverage index",
#        cli_name='--max_lci',
#        default=1000.0,
#        maximum=1000.0
#    ))

    item.add_parameter(FilterThreshold(
        text="min. coverage",
        desc="minimum average coverage",
        cli_name='--min_cov',
        default=0,
        maximum=9999,
        precision=0
    ))

    item.add_parameter(FilterThreshold(
        text="max. coverage",
        desc="maximum average coverage",
        cli_name='--max_cov',
        default=9999,
        maximum=9999,
        precision=0
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


""" plotting methods """


def plot_rld(ax, length_dist, min_length, max_length, read_count,
             length_dist_total):
    """Creates a bar plot of a read length distribution.

    Includes scaled expected distribution based on all reads in file.

    Parameters
    ----------
    ax : Axes
        Axes instance of current plot.
    length_dist : array_like
        Read length distribution of subset of reads.
    min_length : int
        Minimum read length.
    max_length : int
        Maximum read length.
    read_count : int
        Total number of reads.
    length_dist_total : array_like
        Read length distribution of all reads.
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
    """Creates a bar plot of a coverage distribution.

    Parameters
    ----------
    ax : Axes
        Axes instance of current plot.
    depth_dist : array_like
        Coverage depth distribution.
    avg_depth : float
        Mean coverage.
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
    """Creates a bar plot of a scaled coverage distribution.

    Parameters
    ----------
    ax : Axes
        Axes instance of current plot.
    depth_dist : array_like
        coverage depth distribution.
    avg_depth : float
        Mean coverage.
    ref_length : int
        Length of reference in nucleotides.
    max_depth : int
        Maximum coverage depth.
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
    """Creates a bar plot of a cumulative coverage distribution.

    Parameters
    ----------
    ax : Axes
        Axes instance of current plot.
    depth_dist_cumsum : array_like
        Cumulative coverage depth distribution.
    avg_depth : float
        Mean coverage.
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
    """Creates a bar plot of a scaled cumulative coverage distribution.

    Parameters
    ----------
    ax : Axes
        Axes instance of current plot.
    depth_dist_cumperc : array_like
        Scaled cumulative coverage depth distribution.
    avg_depth : float
        Mean coverage.
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
    """Creates a bar plot of a normalized cumulative coverage distribution.

    Includes legend stating average scaled and total depth.

    Parameters
    ----------
    ax : Axes
        Axes instance of current plot.
    depth_dist_cumperc : array_like
        Scaled cumulative coverage depth distribution.
    avg_depth : float
        Mean coverage.
    max_depth : int
        Maximum coverage depth.
    avg_depth_scaled : float
        Scaled mean coverage.
    lci : float
        LCI parameter.
    color : str
        Color name to be used for the bar plot.
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
    """Creates a Lorenz curve plot of a coverage distribution.

    Parameters
    ----------
    ax : Axes
        Axes instance of current plot.
    x : array_like
        Coverage bins.
    Y : array_like
        Aligned bases per coverage bin.
    """
    (gini, auc) = get_gini_auc(x, y)

    ax.set_title("Lorenz")

    # show equal distribution
    ax.plot([0, 1],
            [0, 1],
            color='green',
            label="equal distribution")

    # show actual distribution
    ax.plot(x, y, label="actual distribution")
    ax.fill(x, y, color='gray', alpha=0.2)

    ax.axis([0, 1, 0, 1])

    ax.set_xlabel("fraction of coverage bins")
    ax.set_ylabel("fraction of alignment")
    ax.text(0.05, 0.75, "Gini = %.2f" % (gini,), transform=ax.transAxes)

    ax.legend(loc=2)  # upper left


def plot_lorenz_b2b(ax, x, y):
    """Creates a Lorenz curve plot of a base2base coverage distribution.

    Parameters
    ----------
    ax : Axes
        Axes instance of current plot.
    x : array_like
        reference base positions.
    Y : array_like
        Aligned bases per reference base.
    """
    (gini, auc) = get_gini_auc(x, y)

    ax.set_title("Lorenz base2base")

    # show equal distribution
    ax.plot([0, 1],
            [0, 1],
            color='green',
            label="equal distribution")

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
    """Integrate discrete distribution with stepsize 1 by adding up values.

    Parameters
    ----------
    dist : array_like
        Discrete distribution with stepsize 1.
    limit : int
        Upper limit (exclusive).

    Returns
    -------
    float
        Integral of the distribution between 0 and upper limit.
    """
    return np.sum(dist[0:limit]) / 100.0


def integral_scaled(dist, limit):
    """Integrates scaled discrete distribution with arbitrary stepsize.

    Parameters
    ----------
    dist : array_like
        Scaled discrete distribution with arbitrary stepsize.
    limit : float
        Upper limit (exclusive).

    Returns
    -------
    float
        Integral of the distribution between 0 and upper limit.
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

    stepsize = 1.0 / (dist.size - 1)
    x = stepsize
    for y in np.nditer(dist):
        if limit_scaled > x:
            area += stepsize * y
        else:
            area += (limit_scaled - (x - stepsize)) * y
            break
        x += stepsize

    return area


def lorenzify(depth_dist):
    """Calculates Lorenz curve from coverage distribution.

    Parameters
    ----------
    depth_dist : array_like
        Coverage depth distribution.

    Returns
    -------
    x : array_like
        X coordinates of Lorenz curve.
    y : array_like
        Y coordinates of Lorenz curve.
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
    """Calculate Lorenz curve from base2base coverage distribution.

    Parameters
    ----------
    depth_dist : array_like
        Coverage depth distribution.
    ignore_uncovered : bool
        Ignore bases with zero coverage, defaults to True.

    Returns
    -------
    x : array_like
        X coordinates of Lorenz curve.
    y : array_like
        Y coordinates of Lorenz curve.
    """
    ali_total = 0
    ref_total = 0

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

    # turn lists into arrays and scale them
    b = np.array(ref_bases_list) * 1.0 / ref_total
    v = np.array(ali_bases_list) * 1.0 / ali_total

    triples = np.array([b, v, v/b])
    ttriples = np.transpose(triples)
    tttriples = np.transpose(ttriples[ttriples[:, 2].argsort()])

    x = np.cumsum(tttriples[0])
    y = np.cumsum(tttriples[1])

    # append (0|0) origin to beginning of arrays, scale both axes on the fly
    x = np.append(np.array([0]), x)
    y = np.append(np.array([0]), y)

    return (x, y)


def get_gini_auc(x, y):
    """Calculates Gini coefficient and area under Lorenz curve.

    The Gini coefficient (also known as the Gini index) is a measure of
    statistical dispersion. When applied to the distribution of aligned read
    bases per reference base an even distribution of reads across the reference
    should have a low Gini coefficient (towards 0) while an alignment with all
    reads covering the same reference region should have a high Gini
    coefficient (towards 1).

    Parameters
    ----------
    x : array_like
        X coordinates of a normalized Lorenz distribution.
    y : array_like
        Y coordinates of a normalized Lorenz distribution.

    Returns
    -------
    float
        Gini coefficient. Ranges from 0 for a perfectly even distribution to 1
        for a maximally uneven distribution.
    float
        Integral of the Lorenz curve (area under curve). Maximal value is 0.5
        if the given distribution is uniform.
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

    # calculate Gini coefficient (area under normalized uniform dist is 0.5)
    gini = 1.0 - (2 * auc)

    return (gini, auc)


def covered_length_from_cigar(cigar):
    """Calculates length of reference covered by read from CIGAR operations.

    Note
    ----
    * not counting padding, skipping or insertions into the reference.
    * not counting hard or soft clipped bases of the read

    Parameters
    ----------
    cigar : str
        Unmodified CIGAR string from SAM file.

    Returns
    -------
    int
        Length of the reference sequence.
    """
    regex = re.compile("(\d+)([MIDNSHP=X])")
    length = 0
    for match in regex.finditer(cigar):
        if match.group(2) in ("M", "=", "X", "D"):
            length += int(match.group(1))
    return length


def calc_avg_depth(depth_dist, ignore_uncovered=True):
    """Calculate average depth from a coverage distribution.

    Optionally ignores uncovered bases (first array element).

    Parameters
    ----------
    depth_dist : array_like
        Sorted coverage depth distribution.
    ignore_uncovered : bool, optional
        Ignore bases with zero coverage (first array element), defaults to
        True.
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
    """Executable to filter SAM files for references with uneven coverage.

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
    parser.add_argument('-r', '--read_lengths',
                        required=False,
                        action='store_true',
                        help='analyze read length distributions')
    parser.add_argument('-c', '--covered',
                        required=False,
                        action='store_true',
                        help='covered bases only, ignore uncovered bases')
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
        stats_filename = "${filename}.stats.csv"

    # initialize dicts
    header = []                     # SAM header lines, unmodified
    depths = {}                     # dict of np.array of ints
    ref_lengths = {}                # dict of ints
    read_counts = {}                # dict of ints
    if args.read_lengths:
        read_lenghts = {}           # dict of dict of ints
        read_lenghtsTotal = {}      # dict of ints
    line_count = 0
    positions = {}   # dict of list for references and their line numbers
    buffer = None    # file handle used to buffer complete STDIN
    byte_offset = 0  # offset of first line after end of header
    line_offset = 0

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

        for line_nr, line in enumerate(handle, 0):
            line_count = line_nr + 1
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

                accession = ""
                try:
                    accession = rname_parts[3]
                except IndexError:
                    accession = "unknown"
                    log.warn("no accession in line %s, assigning read to "
                             "accession 'unknown'" % (line_nr + 1))

                # extract reference sequence length from optional ZL field
                ref_length = 0
                try:
                    zl_parts = fields[13].split(":")
                    ref_length = int(zl_parts[2])
                except IndexError:
                    log.error("no ZL field in line" % (line_nr + 1))
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

                # remember occurence of accession and line number(s)
                try:
                    positions[accession].append(line_nr)
                except KeyError:
                    positions[accession] = [line_nr, ]
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
    lines = []
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

            # TODO also calculate Theil index, see
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
                             max_length_total, line_nr + 1, length_dist_total)

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
    log.info("STEP 3: %s %i unevenly covered references from SAM file." %
             (alt[args.discard], len(lines)))

    line_filter(lines, buffer, discard=(args.discard == 0),
                offset=line_offset)
    buffer.close()

    log.info("END of filtering references by coverage, statistics saved to "
             "file %s" % (stats_filename, ))

    exit()

if __name__ == "__main__":
    main()
