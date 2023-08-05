# -*- coding: utf-8 -*-
"""Wrapper for PMDtools score calculation functionality.

.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

""" custom libraries """
from samsifter.models.filter import FilterItem
from samsifter.models.parameter import FilterParameter

""" global variables """
TEXT = "[PMDtools] Calculate PMDS"
DESC = ("Calculates post-mortem degradation scores of reads and writes them "
        "into the DS tags.")


def item():
    """Create item representing this tool in list and tree views.

    Returns
    -------
    FilterItem
        Item for use in item-based list and tree views.
    """
    item = FilterItem(text=TEXT, desc=DESC, icon=FilterItem.ICON_ANALYZER)
    item.set_command('pmdtools_mod --dry --writesamfield --header')

    item.add_parameter(FilterParameter(
        text="verbose",
        desc="print additional information to STDERR",
        cli_name="--verbose",
        default=True,
        active=True
    ))

    item.add_parameter(FilterParameter(
        text="statistics",
        desc="output summarizing statistics to STDERR",
        cli_name="--stats",
        default=False
    ))

    return item
