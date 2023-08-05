#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Dec 18 09:34:28 2014

@author: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

import sys
if not (sys.version_info[0] >= 3):
    print("Error, I need python 3.x or newer")
    exit(1)

""" custom libraries """
from samsifter.models.filter import FilterItem
from samsifter.models.parameter import (FilterParameter, FilterThreshold)

""" global variables """
TEXT = "[PMDtools] Filter reads by % identity"
DESC = ("Filtering reads with insufficient identity to their respective "
        "reference. Identity calculated according to PMDtools, activating all "
        "options will calculate identity according to MALT")


def item():
    """
    Create FilterItem for this filter to be used in list and tree models.
    """
    item = FilterItem(text=TEXT, desc=DESC)

    p_min_identity = FilterThreshold("min. identity",
                                     "minimum identity of read to reference",
                                     "--perc_identity",
#                                     unit='%',
                                     unit=None,
                                     required=True,
                                     active=True)
    p_min_identity.setMinimum(0.00)
    p_min_identity.setDefault(0.95)
    p_min_identity.setMaximum(1.00)
    item.addParameter(p_min_identity)

    p_indels = FilterParameter("include indels",
                               "treat insertions and deletions as mismatches",
                               "--include_deamination",
                               required=False,
                               active=False)
    p_indels.setDefault(False)
    item.addParameter(p_indels)

    p_deamination = FilterParameter("include deamination",
                                    "treat possibly deaminated T>C and A>G "
                                    "pairs as mismatches",
                                    "--include_deamination",
                                    required=False,
                                    active=False)
    p_deamination.setDefault(False)
    item.addParameter(p_deamination)

    p_unknown = FilterParameter("include unknown",
                                "treat Ns in either read or reference as "
                                "mismatch",
                                "--include_unknown",
                                required=False,
                                active=False)
    p_unknown.setDefault(False)
    item.addParameter(p_unknown)

#    p_discard = FilterSwitch("filter direction",
#                             "Keep or discard entries passing the filter "
#                             "criteria?",
#                             "--discard",
#                             options=["discard", "keep"],
#                             required=False,
#                             active=False)
#    p_discard.setDefault(0)
#    item.addParameter(p_discard)

    p_verbose = FilterParameter("verbose",
                                "print additional information to STDERR",
                                "--verbose",
                                required=False,
                                active=True)
    p_verbose.setDefault(True)
    item.addParameter(p_verbose)

#    p_debug = FilterParameter("debug",
#                              "print debug messages to STDERR",
#                              "--debug",
#                              required=False,
#                              active=False)
#    p_debug.setDefault(False)
#    item.addParameter(p_debug)

    p_stats = FilterParameter("statistics",
                              "output summarizing statistics to STDERR",
                              "--stats",
                              required=False,
                              active=False)
    p_stats.setDefault(False)
    item.addParameter(p_stats)

    item.setEditable(False)
    item.setCommand('pmdtools_mod --dry --writesamfield --header')
    return item
