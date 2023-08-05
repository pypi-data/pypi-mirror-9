#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrapper for SAMtools sort

@author: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

import sys
if not (sys.version_info[0] >= 3):
    print("Error, I need python 3.x or newer")
    exit(1)

""" custom libraries """
from samsifter.models.filter import FilterItem

""" global variables """
TEXT = "[SAMtools] Sort by query names"
DESC = ("Resorts entries in a BAM file by their names.")


def item():
    """
    Create FilterItem for this filter to be used in list and tree models.
    """
    item = FilterItem(text=TEXT, desc=DESC, icon=FilterItem.ICON_SORTER)
    item.setEditable(False)

    # input/output is not default (SAM sorted by queryname)
    item.set_input_format('BAM')
    item.set_input_sorting('coordinate')
    item.set_output_format('BAM')
    item.set_output_sorting('queryname')

    item.setCommand('samtools sort -n - tmp -o')
    return item
