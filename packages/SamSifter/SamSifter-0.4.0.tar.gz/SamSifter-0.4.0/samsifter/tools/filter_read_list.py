#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Filters reads by list of QNAMES.

Filtering reads by a list of QNAMES (read identifiers) given in a tab-separated
CSV file.

.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

import sys
if not (sys.version_info[0] >= 3):
    print("Error, I need python 3.x or newer")
    exit(1)

import argparse
import logging as log
import fileinput
import csv
from os.path import basename, splitext

""" custom libraries """
from samsifter.models.filter import FilterItem
from samsifter.models.parameter import (
    FilterParameter, FilterSwitch, FilterFilepath
)
from samsifter.util.arg_sanitation import check_sam, check_csv
from samsifter.util.filters import pattern_filter

""" global variables """
TEXT = "Filter reads by list of QNAMES"
DESC = ("Filtering reads by a list of QNAMES (read identifiers) given in a "
        "tab-separated CSV file.")


def item():
    """Create item representing this tool in list and tree views.

    Returns
    -------
    FilterItem
        Item for use in item-based list and tree views.
    """
    item = FilterItem(text=TEXT, desc=DESC)
    item.set_command(splitext(basename(__file__))[0])

    item.add_parameter(FilterFilepath(
        text="read list file",
        desc="tab-separated CSV file with QNAMES in first column",
        cli_name="--list",
        default="reads.csv",
        extensions=['csv'],
        required=True,
        active=True
    ))

    item.add_parameter(FilterSwitch(
        "filter direction",
        "Keep or discard entries passing the filter "
        "criteria?",
        "--discard",
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
    """Executable to filter SAM files for a list of reads.

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
    parser.add_argument('-l', '--list',
                        type=check_csv,
                        help="tab-separated CSV file with accession numbers "
                        "in first column",
                        required=True)
    parser.add_argument('--discard',
                        type=int,
                        help="keep or discard entries passing the filter "
                             "criteria?",
                        required=False,
                        default=0)
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

    log.info("START of filtering reads by list.")

    # generate pattern list from CSV file
    log.info("STEP 1: generating search pattern from CSV file.")
    patterns = []
    with open(args.list, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            patterns.append(row[0])

    # keep or remove patterns from SAM file
    alt = ["discarding", "keeping"]
    log.info("STEP 2: %s %i reads from SAM file." %
             (alt[args.discard], len(patterns)))
    # open SAM file from either command line argument or STDIN
    if args.input:
        handle = open(args.input, 'r')
    else:
        handle = fileinput.input(remainArgs)

    pattern_filter(patterns, handle, discard=(args.discard == 0))
    log.info("END of filtering reads by list.")

    handle.close()

    exit()

if __name__ == "__main__":
    main()
