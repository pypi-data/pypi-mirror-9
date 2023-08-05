#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 09:34:28 2014

@author: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
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
from samsifter.models.parameter import (FilterParameter, FilterSwitch,
                                        FilterFilepath)
from samsifter.util.arg_sanitation import check_sam, check_csv
from samsifter.util.wrappers import grep

""" global variables """
TEXT = "Filter references by list of accessions"
DESC = ("Filtering references by a list of accession numbers given in a "
        "tab-separated CSV file")


def item():
    """
    Create FilterItem for this filter to be used in list and tree models.
    """
    item = FilterItem(text=TEXT, desc=DESC)

    p_ref_list = FilterFilepath("reference list file",
                                "tab-separated CSV file with accession "
                                "numbers in first column",
                                "--list",
                                extensions=['csv'],
                                to_open=True,
                                required=True,
                                active=False)
    p_ref_list.setDefault("references.csv")
    item.addParameter(p_ref_list)

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

    log.info("START of filtering references by list.")

    # generate pattern list from CSV file
    log.info("STEP 1: generating search pattern from CSV file.")
    patterns = []
    with open(args.list, newline='') as csvfile:
        reader = csv.reader(csvfile, delimiter='\t')
        for row in reader:
            patterns.append("|" + row[0] + "|")

    # keep or remove patterns from SAM file
    alt = ["discarding", "keeping"]
    log.info("STEP 2: %s %i references from SAM file." %
             (alt[args.discard], len(patterns)))
    # open SAM file from either command line argument or STDIN
    if args.input:
        handle = open(args.input, 'r')
    else:
        handle = fileinput.input(remainArgs)

    grep(patterns, handle, discard=(args.discard == 0))
    log.info("END of filtering reads by list.")

    handle.close()

    exit()

if __name__ == "__main__":
    main()
