# -*- coding: utf-8 -*-
"""Wrapper for PMDtools identity filter functionality.

.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

""" custom libraries """
from samsifter.models.filter import FilterItem
from samsifter.models.parameter import (FilterParameter, FilterThreshold)

""" global variables """
TEXT = "[PMDtools] Filter reads by % identity"
DESC = ("Filtering reads with insufficient identity to their respective "
        "reference. Identity calculated according to PMDtools, activating all "
        "options will calculate identity according to MALT")


def item():
    """Create item representing this tool in list and tree views.

    Returns
    -------
    FilterItem
        Item for use in item-based list and tree views.
    """
    item = FilterItem(text=TEXT, desc=DESC)
    item.set_command('pmdtools_mod --dry --writesamfield --header')

    item.add_parameter(FilterThreshold(
        text="min. identity",
        desc="minimum identity of read to reference",
        cli_name="--perc_identity",
        default=0.95,
        maximum=1.00,
        required=True,
        active=True
    ))

    item.add_parameter(FilterParameter(
        text="include indels",
        desc="treat insertions and deletions as mismatches",
        cli_name="--include_deamination",
        default=False
    ))

    item.add_parameter(FilterParameter(
        text="include deamination",
        desc="treat possibly deaminated T>C and A>G pairs as mismatches",
        cli_name="--include_deamination",
        default=False
    ))

    item.add_parameter(FilterParameter(
        text="include unknown",
        desc="treat Ns in either read or reference as mismatch",
        cli_name="--include_unknown",
        default=False
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
