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
TEXT = "[PMDtools] Filter reads by PMDS"
DESC = "Filtering reads by their post-mortem degradation score."


def item():
    """
    Create FilterItem for this filter to be used in list and tree models.
    """
    item = FilterItem(text=TEXT, desc=DESC)

    min_pmd_param = FilterThreshold("min. PMDS",
                                    "minimum post-mortem degradation "
                                    "score (PMDS)",
                                    "--threshold",
                                    unit=None,
                                    required=True,
                                    active=True)
    min_pmd_param.setMinimum(-10)
    min_pmd_param.setMaximum(10)
    min_pmd_param.setDefault(3)
    min_pmd_param.setPrecision(0)
    min_pmd_param.setRequired(True)
    item.addParameter(min_pmd_param)

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
    item.setCommand('pmdtools_mod --writesamfield --header')
    return item
