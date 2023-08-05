#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrapper for SAMtools rmdup

@author: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

import sys
if not (sys.version_info[0] >= 3):
    print("Error, I need python 3.x or newer")
    exit(1)

""" custom libraries """
from samsifter.models.filter import FilterItem
from samsifter.models.parameter import FilterParameter

""" global variables """
TEXT = "[SAMtools] Remove duplicates"
DESC = ("Removes duplicate reads with identical start coordinates.")


def item():
    """
    Create FilterItem for this filter to be used in list and tree models.
    """
    item = FilterItem(text=TEXT, desc=DESC)

    p_single_end = FilterParameter("rmdup for SE reads",
                                   "remove duplicate single-end reads",
                                   '-s',
                                   required=False,
                                   active=True)
    p_single_end.setDefault(True)
    item.addParameter(p_single_end)

    p_paired_end = FilterParameter("treat PE as SE",
                                   "treat paired-end reads as single-end "
                                   "reads",
                                   '-S',
                                   required=False,
                                   active=False)
    p_paired_end.setDefault(False)
    item.addParameter(p_paired_end)

    item.setEditable(False)

    # input/output is not default (SAM sorted by queryname)
    item.set_input_format('BAM')
    item.set_input_sorting('coordinate')
    item.set_output_format('BAM')
    item.set_output_sorting('coordinate')

    item.setCommand('samtools rmdup - -')
    return item
