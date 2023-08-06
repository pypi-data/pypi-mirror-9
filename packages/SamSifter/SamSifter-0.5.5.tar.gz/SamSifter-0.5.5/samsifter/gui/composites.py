# -*- coding: utf-8 -*-
"""
Composed widgets used to visualize filter parameters in a vertical form layout.

.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

import os
from os.path import expanduser, isfile

""" Qt4 imports """
from PyQt4.QtGui import (
    QWidget, QSlider, QHBoxLayout, QLineEdit, QPushButton, QFileDialog, QIcon,
    QRadioButton, QButtonGroup, QLabel, QDoubleSpinBox
)
from PyQt4.QtCore import Qt


class SliderSpinboxCombo(QWidget):
    """
    Slider coupled with Spinbox for setting numerical values between a minimum
    and maximum.
    """

    def __init__(self, parent=None, minimum=0.0, maximum=100.0, default=0.0,
                 precision=2):
        """Initialize a new instance of a SliderSpinboxCombo widget.

        Parameters
        ----------
        parent : QWidget, optional
            Parent Qt4 widget this widget belongs to, defaults to None.
        minimum : float, optional
            Minimum value of the permitted value range, defaults to 0.
        maximum : float, optional
            Maximum value of the permitted value range, defaults to 100.
        default : float, optional
            Default used as preset value in slider and spinbox, defaults to 0.
        precision : int, optional
            Number of decimals for the selected value, defaults to 2
            (eg. ``0.12`` for precision 2 vs. ``0.1`` for precision 1).
        """
        super(QWidget, self).__init__(parent)
        self.minimum = minimum
        self.maximum = maximum
        self.default = default
        if default < minimum:
            self.value = minimum
        elif default > maximum:
            self.value = maximum
        else:
            self.value = default
        self.precision = precision

        self.slider = QSlider(self)
        self.slider.setOrientation(Qt.Horizontal)
        self.slider.setTickPosition(QSlider.TicksBelow)
        self.slider.setObjectName("slider")
        self.slider.setMinimum(0)
        self.slider.setMaximum(10000)
        self.slider.setSingleStep(1)
        self.slider.setTickInterval(max(1000,
                                        10000 / (self.maximum - self.minimum)))
        self.slider.setValue(self.normalize(self.value))

        self.spinner = QDoubleSpinBox()
        self.spinner.setDecimals(self.precision)
        self.spinner.setSingleStep(10 ** (-1 * self.precision))
        self.spinner.setMinimum(self.minimum)
        self.spinner.setMaximum(self.maximum)
        self.spinner.setValue(self.value)
        self.spinner.setObjectName("spinner")

        self.spinner.valueChanged.connect(self.on_spinner_value_change)
        self.slider.valueChanged.connect(self.on_slider_value_change)

        layout = QHBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.slider)
        layout.addWidget(self.spinner)
        self.setLayout(layout)

    def on_spinner_value_change(self, value):
        """Handle changes to the spinbox value.

        Parameters
        ----------
        value : float
            New value of spinbox widget.
        """
        self.value = value
        self.slider.setValue(self.normalize(value))

    def on_slider_value_change(self, value):
        """Handle changes to the slider value.

        Parameters
        ----------
        value : float
            New value of slider widget.
        """
        self.spinner.setValue(self.denormalize(value))

    def normalize(self, value):
        """Translates absolute spinbox values to normalized slider values.

        Parameters
        ----------
        value : float
            Current value of spinbox widget.
        """
        delta = self.maximum - self.minimum
        assert delta > 0
        normalized = ((value - self.minimum) * (10000)) / delta
        return normalized

    def denormalize(self, value):
        """Translates normalized slider values to absolute spinbox values.

        Parameters
        ----------
        value : float
            Current value of slider widget.
        """
        delta = self.maximum - self.minimum
        assert delta > 0
        denormalized = ((value * delta) / (10000)) + self.minimum
        return denormalized

    """ Getters & Setters """

    def get_value(self):
        return self.value

    def set_value(self, value):
        if self.precision == 0:
            self.value = int(value)
        else:
            self.value = value
        # no need to set slider, it is coupled to spinbox
        self.spinner.setValue(value)


class FileChooser(QWidget):
    """
    Combined LineEdit and Pushbutton for standard file dialog to select a file.
    """

    def __init__(self, parent=None, suffix_string="CSV files (*.csv *.CSV)"):
        """Initialize a new instance of a FileChooser.

        Parameters
        ----------
        parent : QWidget, optional
            Parent Qt4 widget this widget belongs to, defaults to None.
        suffix_string : str, optional
            String specifying the default file extensions to be displayed in
            the OS-specific file selection dialog. Should contain a short
            file type description and a list of space-separated file extensions
            with asterisks. The default value of ``CSV files (*.csv *.CSV)``
            sets the dialog to display CSV files only.
        """
        super(QWidget, self).__init__(parent)
        self.suffix_string = suffix_string
        self.filename = None

        self.lineedit = QLineEdit(self)

        self.button = QPushButton(QIcon.fromTheme('document-open'),
                                  "Select file...", self)
        self.button.pressed.connect(self.show_dialog)

        layout = QHBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.lineedit)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def highlight(self, boolean=True):
        """Indicates errors or pending actions by changing background color.

        Parameters
        ----------
        boolean : bool, optional
            Enable highlighting of the QlineEdit widget, defaults to True.
        """
        css = "QLineEdit {background-color: #ffe08c;}"
        if boolean:
            self.lineedit.setStyleSheet(css)
        else:
            self.lineedit.setStyleSheet(None)

    def show_dialog(self):
        """Opens OS-specific file selection dialog in user's home directory."""
        dialog = QFileDialog()
        dialog.setDefaultSuffix(self.suffix_string)
        fname = dialog.getOpenFileName(self, 'Open file',
                                       expanduser("~"),
                                       self.suffix_string + ";;All files (*)"
                                       )
        self.lineedit.setText(fname)
        self.set_filename(fname)

    """ Getters & Setters """

    def get_suffix_string(self):
        return self.suffix_string

    def set_suffix_string(self, suffix_string):
        self.suffix_string = suffix_string

    def get_filename(self):
        return self.filename

    def set_filename(self, filename):
        """Sets a new filename.

        Maintains cursor position and validates the input on the fly. Tooltips
        and highlights of the QLineEdit widget are set to help resolving
        potential errors.

        Parameters
        ----------
        filename : str
            Path to existing and readable input file.
        """

        self.filename = filename

        # validate file
        if not (isfile(filename) and os.access(filename, os.R_OK)):
            self.highlight(True)
            self.lineedit.setToolTip(
                "file either not existing or not readable"
            )
        else:
            self.highlight(False)
            self.lineedit.setToolTip(None)

        cursor = self.lineedit.cursorPosition()
        self.lineedit.setText(filename)
        self.lineedit.setCursorPosition(cursor)


class OptionSwitcher(QWidget):
    """
    Group of coupled radio buttons to choose between exclusive options.

    Defaults to a simple True or False switch but arbitrary lists of options
    are supported and their options internally referenced by list indices. The
    first option in a list is considered the default value.
    """
    def __init__(self, parent=None, options=[True, False]):
        """Initialize a new instance of an optionSwitcher.

        Parameters
        ----------
        parent : QWidget, optional
            Parent Qt4 widget this widget belongs to, defaults to None.
        options : list
            Arbitrary list of options to choose between. Supports any data type
            like numbers, strings, etc. However the list objects have to
            provide short string representations to be properly displayed in
            the GUI form. Defaults to a list with the two options True or
            False.

        """
        super(QWidget, self).__init__(parent)
        self.options = options
        self.current_index = 0
        self.group = QButtonGroup(self)

        layout = QHBoxLayout(self)
        layout.setMargin(0)

        for idx, option in enumerate(self.options):
            lbl = QLabel(str(option), self)
            btn = QRadioButton(self)
            btn.setChecked(idx == self.current_index)
            self.group.addButton(btn, idx)
            layout.addWidget(btn)
            layout.addWidget(lbl)

        self.setLayout(layout)

    """ Getters & Setters """

    def get_options(self):
        return self.options

    def set_options(self, options):
        self.options = options

    def get_current_index(self):
        return self.current_index

    def set_current_index(self, index):
        if 0 <= index and index < len(self.options):
            self.current_index = index
            self.group.button(index).setChecked(True)
