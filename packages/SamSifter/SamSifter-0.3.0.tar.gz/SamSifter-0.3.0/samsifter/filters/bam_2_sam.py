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
TEXT = "[SAMtools] Convert BAM to SAM format"
DESC = ("Converts the binary BAM format to the text-based SAM format.")


def item():
    """
    Create FilterItem for this filter to be used in list and tree models.
    """
    item = FilterItem(text=TEXT, desc=DESC, icon=FilterItem.ICON_CONVERTER)

    p_header = FilterParameter("print header",
                               "include header in output",
                               '-h',
                               required=False,
                               active=True)
    p_header.setDefault(True)
    item.addParameter(p_header)

    item.setEditable(False)

    # input/output is not default (SAM sorted by queryname)
    item.set_input_format('BAM')
    item.set_input_sorting('any')
    item.set_output_format('SAM')
    item.set_output_sorting('as_input')

    item.setCommand('samtools view -')
    return item
