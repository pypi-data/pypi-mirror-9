#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrapper for SAMtools view

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
TEXT = "[SAMtools] Convert SAM to BAM format"
DESC = ("Converts the text-based SAM format to the binary BAM format.")


def item():
    """
    Create FilterItem for this filter to be used in list and tree models.
    """
    item = FilterItem(text=TEXT, desc=DESC, icon=FilterItem.ICON_CONVERTER)

    p_uncompressed = FilterParameter("uncompressed BAM output",
                                     "skip compression of the binary format "
                                     "to speed up following SAMtools steps",
                                     '-u',
                                     required=False,
                                     active=False)
    p_uncompressed.setDefault(False)
    item.addParameter(p_uncompressed)

    item.setEditable(False)

    # input/output is not default (SAM sorted by queryname)
    item.set_input_format('SAM')
    item.set_input_sorting('any')
    item.set_output_format('BAM')
    item.set_output_sorting('as_input')

    item.setCommand('samtools view -S -b -')
    return item
