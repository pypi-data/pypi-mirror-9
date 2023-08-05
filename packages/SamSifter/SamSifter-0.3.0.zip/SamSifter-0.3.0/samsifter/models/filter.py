#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 16:37:21 2014

@author: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

""" Qt4 libraries """
from PyQt4.QtGui import QStandardItem, QIcon

""" custom libraries """
from samsifter.gui.widgets import FilterWidget
from samsifter.resources import resources  #@UnusedImport


SUPPORTED_FORMATS = ['SAM', 'BAM', 'any', 'as_input']
SUPPORTED_SORTINGS = ['unsorted', 'queryname', 'coordinate', 'any', 'as_input']
SUPPORTED_COMPRESSIONS = ['uncompressed', 'gzip', 'any', 'as_input']


class FilterItem(QStandardItem):
    # icon paths correspond to resource entries
    ICON_ANALYZER = ":/x-office-spreadsheet.png"
    ICON_CONVERTER = ":/applications-other.png"
    ICON_FILTER = ":/view-filter.png"
    ICON_SORTER = ":/view-sort-ascending.png"

    def __init__(self, text=None, desc=None, icon=ICON_FILTER):
        if icon is None:
            super(FilterItem, self).__init__(text)
        else:
            super(FilterItem, self).__init__(QIcon(icon), text)
        self.desc = desc
        self.icon_path = icon
        self.command = "tester"
        self.input_format = 'SAM'
        self.input_sorting = 'queryname'
        self.input_compression = 'uncompressed'
        self.output_format = 'SAM'
        self.output_sorting = 'queryname'
        self.output_compression = 'uncompressed'
        self.parameters = []
        self.valid = True

    def clone(self):
        """
        Create new instance with identical settings.
        """
        clone = FilterItem(self.text(), self.desc, self.icon_path)
        clone.setCommand(self.command)
        clone.set_input_format(self.input_format)
        clone.set_input_sorting(self.input_sorting)
        clone.set_input_compression(self.input_compression)
        clone.set_output_format(self.output_format)
        clone.set_output_sorting(self.output_sorting)
        clone.set_output_compression(self.output_compression)
        for param in self.parameters:
            clone.addParameter(param.clone())
        return clone

    def commandline(self, basenames=False):
        """
        Print full bash command line for filter with all parameters.
        """
        cl = self.command
        for param in self.parameters:
            if param.isActive() or param.isRequired():
                cl += " " + param.cli(basenames)
        return cl

    def makeWidget(self):
        """
        Create a FilterWidget visualizing all parameters of this filter.
        """
        return FilterWidget(self)

    def __str__(self):
        return self.text()

    def __repr__(self):
        rep = "\n%s" % self.text()
        rep += "\n- command:\t\t%s" % self.command
        rep += "\n- description:\t%s" % self.desc
        for param in self.parameters:
            rep += repr(param)
        return rep

    """ Getters & Setters """

    def addParameter(self, parameter):
        self.parameters.append(parameter)

    def get_parameters(self):
        return self.parameters

    def setCommand(self, command):
        self.command = command

    def getDesc(self):
        return self.desc

    def setDesc(self, desc):
        self.desc = desc

    def get_icon_path(self):
        return self.icon_path

    def set_icon_path(self, icon_path):
        self.icon_path = icon_path

    def set_input_format(self, fileformat):
        if fileformat in SUPPORTED_FORMATS:
            self.input_format = fileformat

    def get_input_format(self):
        return self.input_format

    def set_output_format(self, fileformat):
        if fileformat in SUPPORTED_FORMATS:
            self.output_format = fileformat

    def get_output_format(self):
        return self.output_format

    def set_input_sorting(self, sorting):
        if sorting in SUPPORTED_SORTINGS:
            self.input_sorting = sorting

    def get_input_sorting(self):
        return self.input_sorting

    def set_output_sorting(self, sorting):
        if sorting in SUPPORTED_SORTINGS:
            self.output_sorting = sorting

    def get_output_sorting(self):
        return self.output_sorting

    def set_input_compression(self, compression):
        if compression in SUPPORTED_COMPRESSIONS:
            self.input_compression = compression

    def get_input_compression(self):
        return self.input_compression

    def set_output_compression(self, compression):
        if compression in SUPPORTED_COMPRESSIONS:
            self.output_compression = compression

    def get_output_compression(self):
        return self.output_compression

    def is_valid(self):
        return self.valid

    def set_valid(self, boolean):
        self.valid = boolean
