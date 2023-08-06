#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Wrapper for SAMtools view functionality to convert SAM to BAM files.

.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

""" custom libraries """
from samsifter.models.filter import FilterItem
from samsifter.models.parameter import FilterParameter

""" global variables """
TEXT = "[SAMtools] Convert SAM to BAM format"
DESC = ("Converts the text-based SAM format to the binary BAM format.")


def item():
    """Create item representing this tool in list and tree views.

    Returns
    -------
    FilterItem
        Item for use in item-based list and tree views.
    """
    item = FilterItem(text=TEXT, desc=DESC, icon=FilterItem.ICON_CONVERTER)
    item.set_command('samtools view -S -b -')

    item.add_parameter(FilterParameter(
        text="uncompressed BAM output",
        desc=("skip compression of the binary format to speed up following "
              "SAMtools steps"),
        cli_name='-u',
        default=False,
        required=False,
        active=False
    ))

    # input/output is not default (SAM sorted by queryname)
    item.set_input_format('SAM')
    item.set_input_sorting('any')
    item.set_output_format('BAM')
    item.set_output_sorting('as_input')

    return item
