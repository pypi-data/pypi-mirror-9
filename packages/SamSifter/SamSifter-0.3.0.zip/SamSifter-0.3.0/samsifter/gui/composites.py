#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Composed widgets used to visualize filter parameters in a form layout.

@author: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

import os
from os.path import expanduser, isfile

""" Qt4 imports """
from PyQt4.QtGui import (QWidget, QSlider, QHBoxLayout, QLineEdit,
                         QPushButton, QFileDialog, QIcon, QRadioButton,
                         QButtonGroup, QLabel, QDoubleSpinBox)
from PyQt4.QtCore import Qt


class SliderSpinboxCombo(QWidget):
    """
    Slider coupled with Spinbox for setting numerical values between a minimum
    and maximum.
    """
    def __init__(self, parent=None, minimum=0.0, maximum=100.0, default=0.0,
                 precision=2):
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

        self.spinner.valueChanged.connect(self.handleSpinnerValueChanged)
        self.slider.valueChanged.connect(self.handleSliderValueChanged)

        layout = QHBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(self.slider)
        layout.addWidget(self.spinner)
        self.setLayout(layout)

    def handleSpinnerValueChanged(self, value):
#        print("spinner:\t" + str(value))
        self.value = value
        self.slider.setValue(self.normalize(value))

    def handleSliderValueChanged(self, value):
#        print("slider:\t" + str(value))
        self.spinner.setValue(self.denormalize(value))

    def normalize(self, value):
        delta = self.maximum - self.minimum
        assert delta > 0
        normalized = ((value - self.minimum) * (10000)) / delta
#        print(str(value) + " >>> " + str(normalized))
        return normalized

    def denormalize(self, value):
        delta = self.maximum - self.minimum
        assert delta > 0
        denormalized = ((value * delta) / (10000)) + self.minimum
#        print(str(denormalized) + " <<< " + str(value))
        return denormalized

    """ Getters & Setters """

    def getValue(self):
        return self.value

    def setValue(self, value):
        if self.precision == 0:
            self.value = int(value)
        else:
            self.value = value
        self.spinner.setValue(value)
#        self.slider.setValue(value)


class FileChooser(QWidget):
    """
    Combined LineEdit and Pushbutton for standard file dialog to select a file.
    """
    def __init__(self, parent=None, suffix_string="CSV files (*.csv *.CSV)"):
        super(QWidget, self).__init__(parent)
        self.suffix_string = suffix_string
        self.filename = None

        self.lineedit = QLineEdit(self)

        self.button = QPushButton(QIcon.fromTheme('document-open'),
                                  "Select file...", self)
        self.button.pressed.connect(self.showDialog)

        layout = QHBoxLayout(self)
        layout.setMargin(0)
#        layout.setSpacing(0)
#        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(self.lineedit)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def highlight(self, boolean=True):
        """
        Indicate errors or pending actions by changing background color.
        """
        css = "QLineEdit {background-color: #ffe08c;}"
        if boolean:
            self.lineedit.setStyleSheet(css)
        else:
            self.lineedit.setStyleSheet(None)

    def showDialog(self):
        dialog = QFileDialog()
        dialog.setDefaultSuffix(self.suffix_string)
        fname = dialog.getOpenFileName(self, 'Open file',
                                       expanduser("~"),
                                       self.suffix_string + ";;All files (*)"
                                       )
        self.lineedit.setText(fname)
        self.setFilename(fname)

    """ Getters & Setters """

    def getSuffixString(self):
        return self.suffix_string

    def setSuffixString(self, suffix_string):
        self.suffix_string = suffix_string

    def getFilename(self):
        return self.filename

    def setFilename(self, filename):
        """
        Set filename while maintaining cursor position and validating input on
        the fly.
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
    """
    def __init__(self, parent=None, options=[True, False]):
        super(QWidget, self).__init__(parent)
        self.options = options
        self.current_index = 0
        self.group = QButtonGroup(self)

        layout = QHBoxLayout(self)
        layout.setMargin(0)
#        layout.setSpacing(0)
#        layout.setAlignment(Qt.AlignTop)

        for idx, option in enumerate(self.options):
            lbl = QLabel(str(option), self)
            btn = QRadioButton(self)
            btn.setChecked(idx == self.current_index)
            self.group.addButton(btn, idx)
            layout.addWidget(btn)
            layout.addWidget(lbl)

        self.setLayout(layout)

    """ Getters & Setters """

    def getOptions(self):
        return self.options

    def setOptions(self, options):
        self.options = options

    def getCurrentIndex(self):
        return self.current_index

    def setCurrentIndex(self, index):
        if 0 <= index and index < len(self.options):
            self.current_index = index
            self.group.button(index).setChecked(True)
