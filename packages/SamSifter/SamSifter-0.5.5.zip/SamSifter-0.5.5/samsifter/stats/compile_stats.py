#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Compilation of statistics for a SAM file.

Usually executed after processing a SAM file with a workflow containing steps
that produce temporary statistics files, eg. the
:py:mod:`samsifter.tools.count_taxon_reads` module. The script takes all
temporary files in the working directory, sorts them by their filenames and
appends their values as new columns to statistics spreadsheet named after the
original input file.

Both the SamSifter GUI as well as the Bash scripts exported from it will
execute this script by default and remove all temporary statistics files when
done.

Note
----
See the script ``enrich_summary`` for details on how to enrich the resulting
file with data from external databases like IMG/M.

See the script ``summarize_stats`` for details on how to summarize multiple
statistics files to quickly inspect the results of a batch run.


.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
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
    """Executes the compilation of temporary statistics files.

    See ``--help`` for details on expected arguments.
    """
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
            match = re.match('%s\.(\d{3})\.csv$' % args.prefix, entry)
#            match = re.fullmatch('%s\.(\d{3})\.csv' % args.prefix, entry)   # new in Python 3.4
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
            # merge stats into sparse array, assumes we never gain new taxa
            readcounts['read_count_%i' % idx] = df['read_count']
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
