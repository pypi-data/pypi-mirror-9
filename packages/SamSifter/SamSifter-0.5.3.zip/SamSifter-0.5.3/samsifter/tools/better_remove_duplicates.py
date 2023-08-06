# -*- coding: utf-8 -*-
"""
Created on Sun Mar  1 10:06:08 2015

.. moduleauthor: aldehoff
"""

# -*- coding: utf-8 -*-
"""
Wrapper for BetterRMDup

.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

""" custom libraries """
from samsifter.models.filter import FilterItem
from samsifter.models.parameter import FilterParameter

""" global variables """
TEXT = "[BetterRMDup] Remove duplicates"
DESC = ("Removes duplicate reads with identical start and stop coordinates.")


def item():
    """Create item representing this tool in list and tree views.

    Returns
    -------
    FilterItem
        Item for use in item-based list and tree views.
    """
    item = FilterItem(text=TEXT, desc=DESC)
#    item.set_command('java -jar BetterRMDupv0.9.jar -')
    item.set_command('betterrmdup -')

    item.add_parameter(FilterParameter(
        text="rmdup for SE reads",
        desc="remove duplicate single-end reads",
        cli_name='-s',
        default=True,
        required=False,
        active=True
    ))

    # input/output is not default (SAM sorted by queryname)
    item.set_input_format('BAM')
    item.set_input_sorting('coordinate')
    item.set_output_format('BAM')
    item.set_output_sorting('coordinate')

    return item
