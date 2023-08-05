#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Basic filtering operations on files.

.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""
import re
import sys
import fileinput


def pattern_filter(patterns, filehandle, discard=True):
    """Emulates grep-like inverse pattern search.

    Emulates the behaviour of ``grep -v -f PATTERNFILE`` and prints only
    non-matching lines to STDOUT. Inverse operation to print only lines
    matching at least one of the patterns by setting discard to False.

    Parameters
    ----------
    patterns : list of str
        List of string patterns to search.
    filehandle : File
        Opened and readable file object.
    discard : bool, optional
        Print only lines matching none of the patterns to STDOUT. Defaults to
        True.

    Returns
    -------
    bool
        True on successful filtering, False on empty pattern list or other
        error.
    """
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


def line_filter(lines, filehandle, discard=True, offset=0):
    """Filters specific lines from a file.

    Prints only lines not contained in list to STDOUT. Inverse operation to
    print only lines contained in list by setting ``discard`` to False.

    Parameters
    ----------
    lines : list of int
        List of line numbers to remove from file. Line numbers are considered
        to be 0-based unless an offset is specified. List can be unsorted and
        duplicates will be removed prior to filtering.
    filehandle : File
        Opened and readable file object.
    discard : bool, optional
        Print only lines matching none of the entries to STDOUT. Defaults to
        True.
    offset: int, optional
        Positive or negative offset for line numbers to be used in case the
        cursor of the filehandle has been placed before or after the start of
        the line numbering. Useful to skip header sections of a file.

    Returns
    -------
    bool
        True on success, False if list of lines is empty or on error.

    Raises
    ------
    Exception
        If first line to be filtered is within the specified offset or if file
        ends before all specified lines are filtered (both indicate wrong use
        of the offset parameter).
    """
    if len(lines) == 0:
        return False

    # sort lines to be filtered and remove duplicate entries
    lines = set(sorted(lines, reverse=True))
    next_line = lines.pop()

    # prevent filtering of negative indices (first line to be filtered is
    # within offset)
    if next_line + offset < 0:
        raise Exception("first filtered line %i < offset line %i"
                        % (next_line, -offset))

    for num, line in enumerate(filehandle):
        if (next_line is not None) and (num == next_line + offset):
            if not discard:
                print(line.rstrip(), file=sys.stdout)
            try:
                next_line = lines.pop()
            except KeyError:
                next_line = None
        else:
            if discard:
                print(line.rstrip(), file=sys.stdout)

    # warn if there are still lines left to be filtered
    if next_line is not None:
        raise Exception("%i unfiltered line(s)" % (len(lines) + 1))

    return True


def main(argv):
    """Simple test of grep and line_filter methods."""
    handle = fileinput.input()
#    textfile = '/home/aldehoff/sandbox/alice.txt'
#    handle = open(textfile, mode='r')

#    patterns = ["lexicon", "fox", "Rabbit"]
#    pattern_filter(patterns, handle, False)

    lines = [3, 4, 7, 1, 1]
    line_filter(lines, handle, False, offset=-2)

if __name__ == '__main__':
    main(sys.argv)
