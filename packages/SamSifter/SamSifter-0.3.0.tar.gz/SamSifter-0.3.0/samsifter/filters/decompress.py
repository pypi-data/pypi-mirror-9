#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Wrapper for GNU Gzip

@author: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

import sys
if not (sys.version_info[0] >= 3):
    print("Error, I need python 3.x or newer")
    exit(1)

""" custom libraries """
from samsifter.models.filter import FilterItem

""" global variables """
TEXT = "[GNU Gzip] Decompress file"
DESC = ("Decompresses the file using GNU Gzip. Should be used only once at "
        "the start of a workflow as frequent compression and decompression "
        "between steps can slow processing down.")


def item():
    """
    Create FilterItem for this filter to be used in list and tree models.
    """
    item = FilterItem(text=TEXT, desc=DESC, icon=FilterItem.ICON_CONVERTER)
    item.setEditable(False)

    # input/output is not default (any input is compressed)
    item.set_input_format('any')
    item.set_input_sorting('any')
    item.set_input_compression('gzip')
    item.set_output_format('as_input')
    item.set_output_sorting('as_input')
    item.set_output_compression('uncompressed')

    item.setCommand('gzip -d')
    return item
