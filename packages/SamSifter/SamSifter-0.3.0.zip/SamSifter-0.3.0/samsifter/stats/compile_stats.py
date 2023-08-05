#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 30 12:25:44 2015

@author: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""
import sys
if not (sys.version_info[0] >= 3):
    print("Error, I need python 3.x or newer")
    exit(1)

import argparse
import logging as log
from os.path import isfile
from os import listdir, remove
import re
import pandas as pd
import numpy as np
pd.set_option('max_columns', 50)


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
    parser.add_argument('-r', '--remove',
                        required=False,
                        action='store_true',
                        help='remove temporary statistics files after use')
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

    # create dict of stats files in working dir
    # using dict instead of list as steps may be omitted
    steps = {}
    for entry in listdir():
        if isfile(entry):
            match = re.fullmatch('%s\.(\d{3})\.csv' % args.prefix, entry)
            if match:
                index = int(match.group(1))
                steps[index] = entry
    log.info("Found %i temporary statistic files with prefix '%s'."
             % (len(steps), args.prefix))

    if len(steps) > 0:
        readcounts = pd.DataFrame(dtype=np.float)
        # sort them by consecutive number
        for idx, filename in sorted(steps.items()):
            log.info("Gathering data from step %i (%s)" % (idx, filename))
            df = pd.read_csv(filename,
                             sep=',',
                             # index_col=0,      # better set index explicitly
                             # engine='python',  # C is faster, supports dtype
                             engine='c',
                             dtype={'taxon_id': str, 'read_count': np.float},
                             quotechar="'",
                             quoting=2)
            df = df.set_index('taxon_id', drop=False)
#            print(df, file=sys.stderr)
            # merge stats into sparse array, assumes we never gain new taxa
            readcounts['read_count_%i' % idx] = df['read_count']
#            print(df['read_count'], file=sys.stderr)
        # save array to CSV
        readcounts.to_csv(sys.stdout,
                          sep=',',
                          header=True,
                          na_rep=0.0,
                          quotechar="'",
                          quoting=2)
    # remove stats files
    if args.remove:
        for filename in steps.values():
            remove(filename)
    exit()


if __name__ == "__main__":
    main()
