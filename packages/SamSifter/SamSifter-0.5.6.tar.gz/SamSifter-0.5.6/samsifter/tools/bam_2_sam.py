# -*- coding: utf-8 -*-
"""Wrapper for SAMtools view functionality converting BAM to SAM files.

.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

""" custom libraries """
from samsifter.models.filter import FilterItem
from samsifter.models.parameter import FilterParameter

""" global variables """
TEXT = "[SAMtools] Convert BAM to SAM format"
DESC = ("Converts the binary BAM format to the text-based SAM format.")


def item():
    """Create item representing this tool in list and tree views.

    Returns
    -------
    FilterItem
        Item for use in item-based list and tree views.
    """
    item = FilterItem(text=TEXT, desc=DESC, icon=FilterItem.ICON_CONVERTER)
    item.set_command('samtools view -')

    item.add_parameter(FilterParameter(
        text="print header",
        desc="include header in output",
        cli_name='-h',
        default=True,
        active=True
    ))

    # input/output is not default (SAM sorted by queryname)
    item.set_input_format('BAM')
    item.set_input_sorting('any')
    item.set_output_format('SAM')
    item.set_output_sorting('as_input')

    return item
