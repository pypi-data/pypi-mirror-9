#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Jan 27 15:34:20 2015

@author: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

import sys

""" Qt4 imports """
from PyQt4.QtGui import (QVBoxLayout, QCheckBox, QDialog, QDialogButtonBox,
                         QLabel, QFormLayout, QRadioButton, QWidget,
                         QButtonGroup)
from PyQt4.QtCore import Qt

""" custom libraries """
from samsifter.gui.composites import SliderSpinboxCombo, FileChooser


class RmaOptionsDialog(QDialog):
    """
    Modal dialog to set SAM2RMA conversion settings.
    """
    def __init__(self, saved_options=None, parent=None):
        super(RmaOptionsDialog, self).__init__(parent)
        self.setSizeGripEnabled(False)
        self.setVisible(False)
        self.setModal(True)
        self.setWindowTitle("SAM2RMA Settings")
        self.options = saved_options
        self.setMinimumWidth(500)

        self.defaults = RmaOptions()
        self.top_percent = SliderSpinboxCombo(
            minimum=0.5,
            maximum=20.0,
            default=self.defaults.get_top_percent(),
            precision=1
        )
        self.min_score = SliderSpinboxCombo(
            minimum=1,
            default=self.defaults.get_min_score(),
            precision=0
        )
        self.max_expected = SliderSpinboxCombo(
            maximum=1.00,
            default=self.defaults.get_max_expected(),
            precision=2)
        self.min_support_percent = SliderSpinboxCombo(
            maximum=10.000,
            default=self.defaults.get_min_support_percent(),
            precision=3
        )
        self.sam2rma_path = FileChooser(
            suffix_string="sam2rma binary (sam2rma)"
        )
        self.sam2rma_path.setFilename(self.defaults.get_sam2rma_path())

        # override defaults with previous settings
        if self.options is not None:
#            print("applying previous settings", file=sys.stderr)
#            print(self.options, file=sys.stderr)
            self.top_percent.setValue(self.options.get_top_percent())
            self.min_score.setValue(self.options.get_min_score())
            self.max_expected.setValue(self.options.get_max_expected())
            self.min_support_percent.setValue(
                self.options.get_min_support_percent()
            )
            self.sam2rma_path.setFilename(self.options.get_sam2rma_path())

        form = QFormLayout(self)
        form.addRow("top [%]:", self.top_percent)
        form.addRow("max. expected:", self.max_expected)
        form.addRow("min. score:", self.min_score)
        form.addRow("min. support [%]", self.min_support_percent)
        form.addRow("SAM2RMA binary:", self.sam2rma_path)

        form_box = QWidget()
        form_box.setLayout(form)

        button_box = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
            | QDialogButtonBox.Reset,
            Qt.Horizontal,
            self
        )

        button_box.button(QDialogButtonBox.Reset).clicked.connect(
            self.reset_form
        )
        button_box.rejected.connect(self.close)
        button_box.accepted.connect(self.saveOptions)

        layout = QVBoxLayout(self)
        layout.addWidget(form_box)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def reset_form(self):
        """
        Resets all form elements to defaults.
        """
        self.top_percent.setValue(self.defaults.get_top_percent())
        self.min_score.setValue(self.defaults.get_min_score())
        self.max_expected.setValue(self.defaults.get_max_expected())
        self.min_support_percent.setValue(
            self.defaults.get_min_support_percent()
        )
        self.sam2rma_path.setFilename(self.defaults.get_sam2rma_path())

    def getOptions(self):
        """
        Shows dialog and returns options unless user decides to cancel.
        """
        self.exec_()
        return self.options

    def saveOptions(self):
        """
        Stores current settings in BashOptions object to be returned.
        """
        self.options = RmaOptions()
        print(self.top_percent.getValue(), file=sys.stderr)
        self.options.set_top_percent(self.top_percent.getValue())
        self.options.set_min_score(self.min_score.getValue())
        self.options.set_max_expected(self.max_expected.getValue())
        self.options.set_min_support_percent(
            self.min_support_percent.getValue()
        )
        self.options.set_sam2rma_path(self.sam2rma_path.getFilename())
        print(self.options, file=sys.stderr)
        self.close()


class RmaOptions():
    """
    Options for the conversion of SAM to RMA files.
    """
    def __init__(
        self,
        # default path for system-wide installation of MEGAN on Linux
        sam2rma_path='/usr/local/megan/tools/sam2rma',
        # default settings in Krause Lab
        top_percent=1,
        max_expected=0.01,
        min_score=50,
        min_support_percent=0.05,
        min_support=1
    ):
        self.sam2rma_path = sam2rma_path
        self.top_percent = top_percent
        self.max_expected = max_expected
        self.min_score = min_score
        self.min_support_percent = min_support_percent
        self.min_support = min_support

#    def __repr__(self):
#        return "top %s" % self.top_percent

    """ Getters & Setters """

    def set_sam2rma_path(self, sam2rma_path):
        self.sam2rma_path = sam2rma_path

    def get_sam2rma_path(self):
        return self.sam2rma_path

    def set_top_percent(self, top_percent):
        self.top_percent = top_percent

    def get_top_percent(self):
        return self.top_percent

    def set_max_expected(self, max_expected):
        self.max_expected = max_expected

    def get_max_expected(self):
        return self.max_expected

    def set_min_score(self, min_score):
        self.min_score = min_score

    def get_min_score(self):
        return self.min_score

    def set_min_support_percent(self, min_support_percent):
        self.min_support_percent = min_support_percent

    def get_min_support_percent(self):
        return self.min_support_percent

    def set_min_support(self, min_support):
        self.min_support = min_support

    def get_min_support(self):
        return self.min_support


class BashOptionsDialog(QDialog):
    """
    Dialog to set bash script export options.
    """
    def __init__(self, parent=None):
        super(BashOptionsDialog, self).__init__(parent)
        self.setSizeGripEnabled(False)
        self.setVisible(False)
        self.setModal(True)
        self.setWindowTitle("Bash Export Options")
        self.options = None

        single_help = ("Enable this to limit processing to the specified "
                       "input file")
        single_label = QLabel("process only the specified file")
        single_label.setToolTip(single_help)
        single_label.setWhatsThis(single_help)
        single_rb = QRadioButton(self)
        single_rb.setToolTip(single_help)
        single_rb.setWhatsThis(single_help)
        single_rb.setChecked(False)

        seq_help = ("Enable this to process an arbitrary number of files "
                    "one after another on a single CPU core")
        seq_label = QLabel("process a batch of files sequentially")
        seq_label.setToolTip(seq_help)
        seq_label.setWhatsThis(seq_help)
        seq_rb = QRadioButton(self)
        seq_rb.setToolTip(seq_help)
        seq_rb.setWhatsThis(seq_help)
        seq_rb.setChecked(False)

        par_help = ("Enable this to process an arbitrary number of files "
                    "as fast as possible using multiple CPU cores; requires "
                    "'GNU parallel'")
        par_label = QLabel("process a batch of files parallelly")
        par_label.setToolTip(par_help)
        par_label.setWhatsThis(par_help)
        par_rb = QRadioButton(self)
        par_rb.setToolTip(par_help)
        par_rb.setWhatsThis(par_help)
        par_rb.setChecked(True)

        self.mode = QButtonGroup(self)
        self.mode.addButton(single_rb)
        self.mode.setId(single_rb, BashOptions.SINGLE_MODE)
        self.mode.addButton(seq_rb)
        self.mode.setId(seq_rb, BashOptions.SEQUENTIAL_MODE)
        self.mode.addButton(par_rb)
        self.mode.addButton(par_rb, BashOptions.PARALLEL_MODE)
        self.mode.setExclusive(True)

        basename_help = ("Enable this if the input files (including CSVs) are "
                         "always located in the current working directory")
        basename_label = QLabel("shorten filepaths to filenames only")
        basename_label.setToolTip(basename_help)
        basename_label.setWhatsThis(basename_help)
        self.basename_cb = QCheckBox(self)
        self.basename_cb.setToolTip(basename_help)
        self.basename_cb.setWhatsThis(basename_help)
        self.basename_cb.setChecked(True)

        print_help = ("Enable this to print all executed commands to STDERR "
                      "(sets bash option '-x')")
        print_label = QLabel("print executed commands")
        print_label.setToolTip(print_help)
        print_label.setWhatsThis(print_help)
        self.print_cb = QCheckBox(self)
        self.print_cb.setToolTip(print_help)
        self.print_cb.setWhatsThis(print_help)
        self.print_cb.setChecked(False)

        stop_help = ("Enable this to stop execution if an error occurs (sets "
                     "bash option '-e')")
        stop_label = QLabel("stop on error")
        stop_label.setToolTip(stop_help)
        stop_label.setWhatsThis(stop_help)
        self.stop_cb = QCheckBox(self)
        self.stop_cb.setToolTip(stop_help)
        self.stop_cb.setWhatsThis(stop_help)
        self.stop_cb.setChecked(True)

        button_box = QDialogButtonBox(QDialogButtonBox.Save
                                      | QDialogButtonBox.Cancel,
                                      Qt.Horizontal,
                                      self)
        button_box.rejected.connect(self.close)
        button_box.accepted.connect(self.saveOptions)

        form = QFormLayout()
        form.addRow(single_rb, single_label)
        form.addRow(seq_rb, seq_label)
        form.addRow(par_rb, par_label)
        form.addRow(self.basename_cb, basename_label)
        form.addRow(self.print_cb, print_label)
        form.addRow(self.stop_cb, stop_label)

        form_box = QWidget()
        form_box.setLayout(form)

        layout = QVBoxLayout(self)
        layout.addWidget(form_box)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def getOptions(self):
        """
        Shows dialog and returns options unless user decides to cancel.
        """
        self.exec_()
        return self.options

    def saveOptions(self):
        """
        Stores current settings in BashOptions object to be returned.
        """
        self.options = BashOptions()
        self.options.set_processing_mode(self.mode.checkedId())
        self.options.set_use_basenames(self.basename_cb.isChecked())
        self.options.set_print_commands(self.print_cb.isChecked())
        self.options.set_stop_on_error(self.stop_cb.isChecked())
        self.close()


class BashOptions():
    """
    Options for the export of a workflow to a bash script.
    """
    SINGLE_MODE = 1
    SEQUENTIAL_MODE = 2
    PARALLEL_MODE = 3

    def __init__(self, use_basenames=True, processing_mode=PARALLEL_MODE,
                 print_commands=False, stop_on_error=True):
        self.use_basenames = use_basenames
        self.processing_mode = processing_mode
        self.print_commands = print_commands
        self.stop_on_error = stop_on_error

    """ Getters & Setters """

    def set_processing_mode(self, mode):
        self.processing_mode = mode

    def get_processing_mode(self):
        return self.processing_mode

    def set_use_basenames(self, boolean):
        self.use_basenames = boolean

    def get_use_basenames(self):
        return self.use_basenames

    def set_print_commands(self, boolean):
        self.print_commands = boolean

    def get_print_commands(self):
        return self.print_commands

    def set_stop_on_error(self, boolean):
        self.stop_on_error = boolean

    def get_stop_on_error(self):
        return self.stop_on_error
