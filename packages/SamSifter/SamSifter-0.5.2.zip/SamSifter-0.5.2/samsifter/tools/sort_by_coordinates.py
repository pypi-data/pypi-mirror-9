# -*- coding: utf-8 -*-
"""Wrapper for SAMtools sort functionality for sorting reads by coordinates.

.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

""" custom libraries """
from samsifter.models.filter import FilterItem

""" global variables """
TEXT = "[SAMtools] Sort by coordinates"
DESC = ("Resorts entries in a BAM file by their coordinates.")


def item():
    """Create item representing this tool in list and tree views.

    Returns
    -------
    FilterItem
        Item for use in item-based list and tree views.
    """
    item = FilterItem(text=TEXT, desc=DESC, icon=FilterItem.ICON_SORTER)

    # input/output is not default (SAM sorted by queryname)
    item.set_input_format('BAM')
    item.set_input_sorting('queryname')
    item.set_output_format('BAM')
    item.set_output_sorting('coordinate')

    item.set_command('samtools sort - tmp -o')
    return item
