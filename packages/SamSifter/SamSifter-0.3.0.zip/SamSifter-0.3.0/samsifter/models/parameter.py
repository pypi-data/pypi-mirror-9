#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 11 01:01:23 2015

@author: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""
from os.path import basename


class FilterParameter():
    """
    Abstraction of a general command line argument for standalone filters.

    Serves as base class for thresholds and filename arguments
    """
    def __init__(self, text, desc, cli_name='--foo', required=False,
                 active=False):
        self.text = text           # label of parameter in GUI
        self.desc = desc           # description of parameter in GUI
        self.cli_name = cli_name   # label of parameter in CLI, eg. '--foo'
        self.required = required   # obligatory parameter, thus on CLI?
        self.active = active       # changed parameter, thus on CLI?

        self.default = None        # required for GUI widget presets
        self.value = None          # set in GUI, otherwise default is used

    def clone(self):
        """
        Create new instance with identical settings.
        """
        clone = FilterParameter(self.text, self.desc, self.cli_name,
                                self.required, self.active)
        clone.setDefault(self.default)
        clone.setValue(self.value)
        # deactivate if activated by previous settings
        clone.setActive(self.active)
        return clone

    def __str__(self):
        return self.text

    def __repr__(self):
        rep = "\n -> %s" % self.text
        rep += "\n    - description:\t%s" % self.desc
        rep += "\n    - default:\t%s" % self.default
        rep += "\n    - value\t:\t%s" % self.value
        rep += "\n    - CLI name:\t%s" % self.cli_name
        rep += "\n    - required:\t%s" % self.required
        rep += "\n    - active:\t%s" % self.active
        return rep

    def cli(self, basenames=False):
        if self.active or self.required:
            return self.cli_name
        else:
            return ""

    def getFormText(self):
        return self.text + ":"

    """ Getters & Setters """

    def getDesc(self):
        return self.desc

    def setDesc(self, desc):
        self.desc = desc

    def setValue(self, value):
        self.value = value
        # here: value and active status are linked, override in derived classes
        self.active = value

    def getValue(self):
        if self.value is None:
            return self.default
        else:
            return self.value

    def setDefault(self, default):
        self.default = default
        if self.value is None:
            self.value = default

    def getDefault(self):
        return self.default

    def getCliName(self):
        return self.cli_name

    def setCliName(self, cli_name):
        self.cli_name = cli_name

    def isActive(self):
        return self.active

    def setActive(self, active=True):
        """
        Activate parameter to force showing in on the commandline.
        """
        self.active = active

    def isRequired(self):
        return self.required

    def setRequired(self, required=True):
        self.required = required


class FilterThreshold(FilterParameter):
    """
    Abstraction of a command line parameter with treshold function.
    """
    def __init__(self, text, desc, cli_name='--foo', unit=None, required=False,
                 active=False):
        super(FilterThreshold, self).__init__(text, desc, cli_name, required,
                                              active)
        self.unit = unit
        self.minimum = 0.00
        self.maximum = 100.00
        self.default = 5.00
        self.precision = 2

    def clone(self):
        """
        Create new instance with identical settings.
        """
        clone = FilterThreshold(self.text, self.desc, self.cli_name, self.unit,
                                self.required, self.active)
        clone.setMinimum(self.minimum)
        clone.setMaximum(self.maximum)
        clone.setDefault(self.default)
        clone.setPrecision(self.precision)
        clone.setValue(self.value)
        # deactivate if activated by previous settings
        clone.setActive(self.active)
        return clone

    def getFormText(self):
        text = self.text
        if self.unit is not None:
            text += " [" + self.unit + "]"
        text += ":"
        return text

    def __repr__(self):
        rep = super(FilterThreshold, self).__repr__()
        rep += "\n    - unit:\t\t%s" % self.unit
        rep += "\n    - minimum:\t%s" % self.minimum
        rep += "\n    - maximum:\t%s" % self.maximum
        rep += "\n    - precision:\t%s" % self.precision
        return rep

    def cli(self, basenames=False):
        if self.active or self.required:
            if self.value is None:
                return "%s %s" % (self.cli_name, self.default)
            else:
                return "%s %s" % (self.cli_name, self.value)
        else:
            return ""

    """ Getters & Setters """

    def getMaximum(self):
        return self.maximum

    def setMaximum(self, maximum):
        self.maximum = maximum

    def getMinimum(self):
        return self.minimum

    def setMinimum(self, minimum):
        self.minimum = minimum

    def getUnit(self):
        return self.unit

    def setUnit(self, unit):
        self.unit = unit

    def getPrecision(self):
        return self.precision

    def setPrecision(self, precision):
        self.precision = precision

    def setValue(self, value):
        """
        Specialized from parent class to consider value precision.
        """
        if self.precision == 0:
            self.value = int(value)
        else:
            self.value = value
        # active parameter once value is changed
        self.active = self.value is not None


class FilterFilepath(FilterParameter):
    def __init__(self, text, desc, cli_name='--foo', extensions=['csv'],
                 to_open=True, required=False, active=False):
        super(FilterFilepath, self).__init__(text, desc, cli_name, required,
                                             active)
        self.extensions = extensions
        self.to_open = to_open

    def clone(self):
        """
        Create new instance with identical settings.
        """
        clone = FilterFilepath(self.text, self.desc, self.cli_name,
                               self.extensions, self.to_open,
                               self.required, self.active)
        clone.setDefault(self.default)
        clone.setValue(self.value)
        # deactivate if activated by previous settings
        clone.setActive(self.active)
        return clone

    def __repr__(self):
        rep = super(FilterFilepath, self).__repr__()
        rep += "\n    - extensions:\t%s" % self.extensions
        rep += "\n    - to open:\t%s" % self.to_open
        return rep

    def cli(self, basenames=False):
        if self.active or self.required:
            if self.value is None:
                if basenames:
                    return "%s %s" % (self.cli_name, basename(self.default))
                else:
                    return "%s %s" % (self.cli_name, self.default)
            else:
                if basenames:
                    return "%s %s" % (self.cli_name, basename(self.value))
                else:
                    return "%s %s" % (self.cli_name, self.value)
        else:
            return ""

    """ Getters & Setters """

    def setValue(self, value):
        self.value = value
        # active parameter once value is changed
        self.active = self.value is not None

    def getExtensions(self):
        return self.extensions

    def setExtensions(self, extensions):
        self.extensions = extensions


class FilterSwitch(FilterParameter):
    """
    Abstraction of a command line switch for a list of exclusive options.

    Defaults to a binary switch between True and False.
    """
    def __init__(self, text, desc, cli_name='--foo', options=[True, False],
                 required=False, active=False):
        super(FilterSwitch, self).__init__(text, desc, cli_name, required,
                                           active)
        self.options = options

    def clone(self):
        """
        Create new instance with identical settings.
        """
        clone = FilterSwitch(self.text, self.desc, self.cli_name,
                             self.options,
                             self.required, self.active)
        clone.setDefault(self.default)
        clone.setValue(self.value)
        # deactivate if activated by previous settings
        clone.setActive(self.active)
        return clone

    def __repr__(self):
        rep = super(FilterSwitch, self).__repr__()
        rep += "\n    - options\t%s" % self.options
        return rep

    def cli(self, basenames=False):
        if self.active or self.required:
            if self.value is None:
                return "%s %s" % (self.cli_name, self.default)
            else:
                return "%s %s" % (self.cli_name, self.value)
        else:
            return ""

    """ Getters & Setters """

    def setValue(self, value):
        self.value = value
        # active parameter once value is changed
        self.active = self.value is not None

    def getOption(self, index):
        try:
            return self.options[index]
        except IndexError:
            return None

    def getOptions(self):
        return self.options

    def setOptions(self, options):
        self.options = options
