# -*- coding: utf-8 -*-
"""Wrapper for PMDtools ancient read filter functionality.

.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

""" custom libraries """
from samsifter.models.filter import FilterItem
from samsifter.models.parameter import (FilterParameter, FilterThreshold)

""" global variables """
TEXT = "[PMDtools] Filter reads by PMDS"
DESC = "Filtering reads by their post-mortem degradation score."


def item():
    """Create item representing this tool in list and tree views.

    Returns
    -------
    FilterItem
        Item for use in item-based list and tree views.
    """
    item = FilterItem(text=TEXT, desc=DESC)
    item.set_command('pmdtools_mod --writesamfield --header')

    item.add_parameter(FilterThreshold(
        text="min. PMDS",
        desc="minimum post-mortem degradation score (PMDS)",
        cli_name="--threshold",
        default=3,
        minimum=-10,
        maximum=10,
        precision=0,
        required=True,
        active=True
    ))

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
