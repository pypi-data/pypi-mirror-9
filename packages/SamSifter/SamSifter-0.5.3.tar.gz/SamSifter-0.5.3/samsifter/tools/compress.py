# -*- coding: utf-8 -*-
"""Wrapper for GNU Gzip compression functionality.

.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

""" custom libraries """
from samsifter.models.filter import FilterItem

""" global variables """
TEXT = "[GNU gzip] Compress file"
DESC = ("Compresses the file using GNU gzip. Should be used only once at "
        "the end of a workflow as frequent compression and decompression "
        "between steps can slow processing down.")


def item():
    """Create item representing this tool in list and tree views.

    Returns
    -------
    FilterItem
        Item for use in item-based list and tree views.
    """
    item = FilterItem(text=TEXT, desc=DESC, icon=FilterItem.ICON_CONVERTER)
    item.set_command('gzip -c')

    # input/output is not default (any input is compressed)
    item.set_input_format('any')
    item.set_input_sorting('any')
    item.set_input_compression('uncompressed')
    item.set_output_format('as_input')
    item.set_output_sorting('as_input')
    item.set_output_compression('gzip')

    return item
