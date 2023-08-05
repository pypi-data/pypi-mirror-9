#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 23 19:29:27 2014

@author: aldehoff
"""
import re
import sys
import fileinput


def grep(patterns, filehandle, discard=True):
    if len(patterns) == 0:
        return False

    # create long search string of patterns separated by | (OR)
    # escape '|' in individual patterns, eg. for taxa and references
    searchstring = re.escape(patterns[0])
    for pattern in patterns[1:]:
        searchstring += "|" + re.escape(pattern)

#    print("search string: %s\n" % searchstring, file=sys.stderr)

    for line in filehandle:
        if line.startswith('@'):
            print(line.rstrip(), file=sys.stdout)
        else:
            result = re.search(searchstring, line)
            if result:
                if not discard:
                    print(line.rstrip(), file=sys.stdout)
            else:
                if discard:
                    print(line.rstrip(), file=sys.stdout)
    return True


def filter_lines(filename, line_numbers):
    """
    Filter a text string by list of line numbers.
    """
    filtered_lines = []
    with open(filename) as handle:
        for num, line in enumerate(handle):
            if num not in line_numbers:
                filtered_lines.append(line)
    return filtered_lines


def main(argv):
    """
    Test of grep method.
    """
    handle = fileinput.input()
#    textfile = '/home/aldehoff/sandbox/alice.txt'
#    handle = open(textfile, mode='r')

    patterns = ["lexicon", "fox", "Rabbit"]
    grep(patterns, handle, False)

if __name__ == '__main__':
    main(sys.argv)
