#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Feb  1 18:50:57 2015

@author: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""
import sys
if not (sys.version_info[0] >= 3):
    print("Error, I need python 3.x or newer")
    exit(1)

import argparse
import logging as log
from os.path import isfile
from os import listdir
import re
import pandas as pd
import numpy as np


def main():
    # parse arguments
    parser = argparse.ArgumentParser(description="compile statistics from "
                                     "temporary files")
    parser.add_argument('-v', '--verbose',
                        required=False,
                        action='store_true',
                        help='print additional information to STDERR')
    parser.add_argument('-d', '--debug',
                        required=False,
                        action='store_true',
                        help='print debug messages to STDERR')
    parser.add_argument('-p', '--prefix',
                        required=False,
                        default='reads_per_taxon',
                        help='prefix of temporary statistics files')
    (args, remainArgs) = parser.parse_known_args()

    # configure logging
    if args.verbose:
        log.basicConfig(format="%(levelname)s: %(message)s", level=log.DEBUG)
    else:
        log.basicConfig(format="%(levelname)s: %(message)s")

    # create list of stats files in working dir
    files = []
    for entry in listdir():
        if isfile(entry):
            match = re.fullmatch('.*\.sifted\.csv', entry)
            if match:
                files.append(match.group(0))
    log.info("Found %i statistic files." % len(files))

    if len(files) > 0:
        summary = pd.DataFrame(dtype=np.float)
        for filename in sorted(files):
            log.info("Gathering data from file %s" % filename)
            # read file
            df = pd.read_csv(filename,
                             sep=',',
                             # index_col=0,      # better set index explicitly
                             # engine='python',  # C is faster, supports dtype
                             engine='c',
                             dtype={'taxon_id': str},
                             quotechar="'",
                             quoting=2)
            df = df.set_index('taxon_id', drop=False)
            # identify last column
            redux = df.ix[:, -1:]
            redux.columns = [filename]
            # filter taxa without reads
            filtered = redux[redux[filename] > 0]
            # merge it with summary file (outer join)
            summary = pd.concat([summary, filtered], axis=1)

        # save summary to CSV
        summary.to_csv(sys.stdout,
                       sep=',',
                       header=True,
                       # na_rep=0.0,
                       quotechar="'",
                       quoting=2)

    exit()

if __name__ == "__main__":
    main()
