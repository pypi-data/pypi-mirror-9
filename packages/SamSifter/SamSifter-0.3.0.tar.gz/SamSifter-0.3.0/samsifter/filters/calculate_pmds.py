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
from samsifter.models.parameter import FilterParameter

""" global variables """
TEXT = "[PMDtools] Calculate PMDS"
DESC = ("Calculates post-mortem degradation scores of reads and writes them "
        "into the DS tags.")


def item():
    """
    Create FilterItem for this filter to be used in list and tree models.
    """
    item = FilterItem(text=TEXT, desc=DESC, icon=FilterItem.ICON_ANALYZER)

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
