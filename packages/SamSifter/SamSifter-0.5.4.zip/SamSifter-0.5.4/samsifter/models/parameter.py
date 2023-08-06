# -*- coding: utf-8 -*-
"""
Different types of command line parameters.

.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""
from os.path import basename


class FilterParameter():
    """Abstraction of a general command line argument for standalone filters.

    Serves as base class for thresholds and filepath arguments.
    """
    def __init__(self, text, desc, cli_name, default, value=None,
                 required=False, active=False):
        """Initialize new instance of FilterParameter.

        Parameters
        ----------
        text : str
            Short label of parameter in GUI, should not exceed one line.
        desc : str
            Longer description of parameter in GUI, should explain details of
            usage.
        cli_name : str
            Name of parameter in CLI, eg. ``--foo``
        default : str
            Default value, required for GUI widget presets.
        value : str, optional
            Parameter value set by GUI elements, default value is used if this
            is (by default) not set.
        required : bool, optional
            Is parameter required to run program? Defaults to False.
        active : bool, optional
            Is parameter activated? Defaults to False.
        """
        self.text = text
        self.desc = desc
        self.cli_name = cli_name
        self.default = default
        self.value = value
        self.required = required
        self.active = active        # should be set after value

    def clone(self):
        """Create new instance with identical settings.

        Returns
        -------
        FilterParameter
            Exact clone of this parameter.
        """
        return FilterParameter(
            self.text, self.desc, self.cli_name, self.default, self.value,
            self.required, self.active
        )

    def __str__(self):
        """String representation of this parameter."""
        return self.text

    def __repr__(self):
        """Representation of this parameter for debugging."""
        rep = "\n -> %s" % self.text
        rep += "\n    - description:\t%s" % self.desc
        rep += "\n    - default:\t%s" % self.default
        rep += "\n    - value\t:\t%s" % self.value
        rep += "\n    - CLI name:\t%s" % self.cli_name
        rep += "\n    - required:\t%s" % self.required
        rep += "\n    - active:\t%s" % self.active
        return rep

    def cli(self, basenames=False):
        """Representation of this parameter on command line interface."""
        if self.active or self.required:
            return self.cli_name
        else:
            return ""

    def get_form_text(self):
        """Representation of this parameter in form layouts."""
        return self.text + ":"

    """ Getters & Setters """

    def get_description(self):
        return self.desc

    def set_description(self, desc):
        self.desc = desc

    def set_value(self, value):
        self.value = value
        # here: value and active status are linked, override in derived classes
        self.active = value

    def get_value(self):
        if self.value is None:
            return self.default
        else:
            return self.value

    def set_default(self, default):
        self.default = default
        if self.value is None:
            self.value = default

    def get_default(self):
        return self.default

    def get_cli_name(self):
        return self.cli_name

    def set_cli_name(self, cli_name):
        self.cli_name = cli_name

    def is_active(self):
        return self.active

    def set_active(self, active=True):
        """Activate parameter to force showing it on the commandline."""
        self.active = active

    def is_required(self):
        return self.required

    def set_required(self, required=True):
        self.required = required


class FilterThreshold(FilterParameter):
    """Abstraction of a numerical command line parameter used as treshold.

    Extends filter parameter by minimum and maximum of permitted value range
    with variable precision and optional unit.
    """

    def __init__(self, text, desc, cli_name, default=5.00, minimum=0.00,
                 maximum=100.00, precision=2, unit=None, value=None,
                 required=False, active=False):
        """Initialize new instance of FilterThreshold.

        Parameters
        ----------
        text : str
            Short label of parameter in GUI, should not exceed one line.
        desc : str
            Longer description of parameter in GUI, should explain details of
            usage.
        cli_name : str
            Name of parameter in CLI, eg. ``--foo``
        default : float, optional
            Default value, required for GUI widget presets; defaults to 5.
        minimum : float, optional
            Minimum of permitted value range, defaults to 0.
        maximum : float, optional
            Maximum of permitted value range, defaults to 100.
        precision : int, optional
            Number of required decimals for values, defaults to 2
            (eg. ``0.12``)
        unit : str, optional
            Value unit, will be used in labels within square brackets (eg.
            ``[kB]``)
        value : float, optional
            Parameter value set by GUI elements, default value is used if this
            is (by default) not set.
        required : bool, optional
            Is parameter required to run program? Defaults to False.
        active : bool, optional
            Is parameter activated? Defaults to False.
        """
        super(FilterThreshold, self).__init__(
            text, desc, cli_name, default, value, required, active
        )
        self.unit = unit
        self.minimum = minimum
        self.maximum = maximum
        self.precision = precision

    def clone(self):
        """Create new instance with identical settings.

        Returns
        -------
        FilterThreshold
            Exact clone of this parameter.
        """
        return FilterThreshold(
            self.text, self.desc, self.cli_name, self.default, self.minimum,
            self.maximum, self.precision, self.unit, self.value, self.required,
            self.active
        )

    def get_form_text(self):
        """Representation of this parameter in form layouts.

        Overrides base method and provides additional information on unit.
        """
        text = self.text
        if self.unit is not None:
            text += " [" + self.unit + "]"
        text += ":"
        return text

    def __repr__(self):
        """Representation of this parameter for debugging.

        Extends base method with additional attributes.
        """
        rep = super(FilterThreshold, self).__repr__()
        rep += "\n    - unit:\t\t%s" % self.unit
        rep += "\n    - minimum:\t%s" % self.minimum
        rep += "\n    - maximum:\t%s" % self.maximum
        rep += "\n    - precision:\t%s" % self.precision
        return rep

    def cli(self, basenames=False):
        """Representation of this parameter on command line interface.

        Overrides base method to handle unset values.
        """
        if self.active or self.required:
            if self.value is None:
                return "%s %s" % (self.cli_name, self.default)
            else:
                return "%s %s" % (self.cli_name, self.value)
        else:
            return ""

    """ Getters & Setters """

    def get_maximum(self):
        return self.maximum

    def set_maximum(self, maximum):
        self.maximum = maximum

    def get_minimum(self):
        return self.minimum

    def set_minimum(self, minimum):
        self.minimum = minimum

    def get_unit(self):
        return self.unit

    def set_unit(self, unit):
        self.unit = unit

    def get_precision(self):
        return self.precision

    def set_precision(self, precision):
        self.precision = precision

    def set_value(self, value):
        """Set value of parameter.

        Overriding base class to consider value precision.
        """
        if self.precision == 0:
            self.value = int(value)
        else:
            self.value = value
        # active parameter once value is changed
        self.active = self.value is not None


class FilterFilepath(FilterParameter):
    """Parameter setting filepath for input or output file.

    Extends parameter base class with a list of supported file extensions and
    requirements for read and write access.
    """
    def __init__(self, text, desc, cli_name, default, extensions=['csv'],
                 readable=True, writable=False, value=None, required=False,
                 active=False):
        super(FilterFilepath, self).__init__(
            text, desc, cli_name, default, value, required, active
        )
        self.extensions = extensions
        self.readable = readable
        self.writable = writable

    def clone(self):
        """Create new instance with identical settings.

        Returns
        -------
        FilterParameter
            An exact copy of this instance.
        """
        return FilterFilepath(
            self.text, self.desc, self.cli_name, self.default, self.extensions,
            self.readable, self.writable, self.value, self.required,
            self.active
        )

    def __repr__(self):
        """Representation of this parameter for debugging.

        Extends base method with additional attributes.
        """
        rep = super(FilterFilepath, self).__repr__()
        rep += "\n    - extensions:\t%s" % self.extensions
        rep += "\n    - readable:\t%s" % self.readable
        rep += "\n    - writable:\t%s" % self.writable

        return rep

    def cli(self, basenames=False):
        """Representation of this parameter on command line interface.

        Overrides base method to handle option for shortened filepaths.

        Parameters
        ----------
        basenames : bool, optional
            Shorten file paths to filename only, defaults to False.

        Returns
        -------
        str
            Full command line argument for this parameter with optionally
            shortened filenames.
        """
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

    def set_value(self, value):
        """Set parameter value.

        Overrides base method to active parameter only when value has changed.
        """
        self.value = value
        # active parameter once value is changed
        self.active = self.value is not None

    def get_extensions(self):
        return self.extensions

    def set_extensions(self, extensions):
        self.extensions = extensions


class FilterSwitch(FilterParameter):
    """Command line switch for a list of exclusive options.

    Extends base class with a list of selectable options. Defaults to a simple
    binary switch between True and False.
    """
    def __init__(self, text, desc, cli_name, default, options=[True, False],
                 value=None, required=False, active=False):
        super(FilterSwitch, self).__init__(
            text, desc, cli_name, default, value, required, active
        )
        self.options = options

    def clone(self):
        """Create new instance with identical settings.

        Returns
        -------
        FilterSwitch
            An exact copy of this instance.
        """
        return FilterSwitch(
            self.text, self.desc, self.cli_name, self.default, self.options,
            self.value, self.required, self.active
        )

    def __repr__(self):
        """Representation of this parameter for debugging.

        Extends base method with additional attributes.
        """
        rep = super(FilterSwitch, self).__repr__()
        rep += "\n    - options\t%s" % self.options
        return rep

    def cli(self, basenames=False):
        """Representation of this parameter on command line interface.

        Overrides base method to handle unset values.
        """
        if self.active or self.required:
            if self.value is None:
                return "%s %s" % (self.cli_name, self.default)
            else:
                return "%s %s" % (self.cli_name, self.value)
        else:
            return ""

    """ Getters & Setters """

    def set_value(self, value):
        """Set parameter value.

        Overrides base method to active parameter only when value has changed.
        """
        self.value = value
        # active parameter once value is changed
        self.active = self.value is not None

    def get_option(self, index):
        """Get specific option out of the available options.

        Parameters
        ----------
        index : int
            Index of option in list of options.

        Returns
        -------
        str
            Desired option (or None on invalid index)
        """
        try:
            return self.options[index]
        except IndexError:
            return None

    def get_options(self):
        return self.options

    def set_options(self, options):
        self.options = options
