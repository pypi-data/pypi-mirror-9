#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 12 16:41:29 2014

@author: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

from os.path import expanduser

""" Qt4 imports """
from PyQt4.QtGui import (
    QWidget, QFileDialog, QGridLayout, QPushButton, QLineEdit, QIcon, QLabel,
    QVBoxLayout, QFormLayout, QCheckBox, QTabWidget
)
from PyQt4.QtCore import (QRect, QSize, pyqtSignal)

""" custom libraries """
from samsifter.gui.composites import (
    SliderSpinboxCombo, FileChooser, OptionSwitcher
)


class OutputWidget(QWidget):
    """
    Representation of file output action in GUI.
    """
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.setGeometry(QRect(10, 1, 381, 51))
        self.setObjectName("output")

        self.icon = QIcon.fromTheme('document-save-as')
        self.icon_label = QLabel()
        self.icon_label.setPixmap(self.icon.pixmap(
            self.icon.actualSize(QSize(32, 32))))

        self.label = QLabel("Output")
        self.file_entry = QLineEdit()
        self.file_btn = QPushButton("Save as...")
        self.file_btn.pressed.connect(self.showDialog)

        self.compile_box = QCheckBox("combine statistics")
        self.compile_box.setToolTip(
            "combine any temporary statistic files into one CSV"
        )
        self.compile_box.setChecked(True)

        self.sam2rma_box = QCheckBox("create RMA file")
        self.sam2rma_box.setToolTip(
            "create RMA file for quick inspection in MEGAN (requires MEGAN "
            "5.8.3 or newer)"
        )
        self.sam2rma_box.setChecked(False)

        self.sam2rma_btn = QPushButton(
            QIcon.fromTheme('preferences-other'), "Settings..."
        )

        self.grid = QGridLayout(self)
        self.grid.addWidget(self.icon_label, 0, 0, 1, 1)
        self.grid.addWidget(self.label, 0, 1, 1, 1)
        self.grid.addWidget(self.file_entry, 0, 2, 1, 1)
        self.grid.addWidget(self.file_btn, 0, 3, 1, 1)
        self.grid.addWidget(self.sam2rma_box, 1, 1, 1, 2)
        self.grid.addWidget(self.sam2rma_btn, 1, 3, 1, 1)
#        self.grid.addWidget(self.compile_box, 2, 1, 1, 2)
        self.setLayout(self.grid)

    def showDialog(self):
        dialog = QFileDialog()
        dialog.setDefaultSuffix('SAM files (*.sam)')
        fname = dialog.getSaveFileName(
            self, 'Save as', expanduser("~"),
            "SAM (*.sam);;zipped SAM (*.sam.gz);;BAM (*.bam)"
        )
        self.file_entry.setText(fname)

    def set_filename(self, filename):
        """
        Update filename in text box while retaining current cursor position.
        """
        cursor = self.file_entry.cursorPosition()
        self.file_entry.setText(filename)
        self.file_entry.setCursorPosition(cursor)

    def highlight(self, boolean=True):
        """
        Indicate errors or pending actions by changing background color.
        """
        css = "QLineEdit {background-color: #ffe08c;}"
        if boolean:
            self.file_entry.setStyleSheet(css)
        else:
            self.file_entry.setStyleSheet(None)


class InputWidget(QWidget):
    """
    Representation of file input action in GUI.
    """
    def __init__(self, parent=None):
        super(QWidget, self).__init__(parent)
        self.setGeometry(QRect(10, 1, 381, 51))
        self.setObjectName("input")

        self.icon = QIcon.fromTheme('document-open')
        self.icon_label = QLabel()
        self.icon_label.setPixmap(self.icon.pixmap(
            self.icon.actualSize(QSize(32, 32))))
        self.label = QLabel("Input")
        self.file_entry = QLineEdit()
        self.file_btn = QPushButton("Open...")
        self.file_btn.pressed.connect(self.showDialog)

        self.grid = QGridLayout(self)
        self.grid.addWidget(self.icon_label, 0, 0, 1, 1)
        self.grid.addWidget(self.label, 0, 1, 1, 1)
        self.grid.addWidget(self.file_entry, 0, 2, 1, 1)
        self.grid.addWidget(self.file_btn, 0, 3, 1, 1)
        self.setLayout(self.grid)

    def showDialog(self):
        dialog = QFileDialog()
        dialog.setDefaultSuffix('SAM/BAM (*.sam *.SAM *.sam.gz *.SAM.GZ *.bam *.BAM)')
        fname = dialog.getOpenFileName(
            self, 'Open file', expanduser("~"),
            "SAM/BAM (*.sam *.SAM *.sam.gz *.SAM.GZ *.bam *.BAM);;SAM (*.sam *.SAM);;zipped SAM (*.sam.gz *.SAM.GZ);;BAM (*.bam *.BAM);;All files (*)"
        )
        self.file_entry.setText(fname)

    def set_filename(self, filename):
        """
        Update filename in text box while retaining current cursor position.
        """
        cursor = self.file_entry.cursorPosition()
        self.file_entry.setText(filename)
        self.file_entry.setCursorPosition(cursor)

    def highlight(self, boolean=True):
        """
        Indicate errors or pending actions by changing background color.
        """
        css = "QLineEdit {background-color: #ffe08c;}"
        if boolean:
            self.file_entry.setStyleSheet(css)
        else:
            self.file_entry.setStyleSheet(None)


class FilterWidget(QWidget):
    """
    Representation of a filter action in GUI.
    """
    value_changed = pyqtSignal(str, name='value_changed')

    def __init__(self, item, parent=None):
        super().__init__(parent)
        self.item = item

        self.setGeometry(QRect(10, 1, 381, 51))
        self.setObjectName("widget")

        """
        Filter label and description
        """
        title = QLabel(self.item.text())
        title.setWordWrap(True)
        description = QLabel(self.item.getDesc())
        description.setWordWrap(True)

        # compression labels
        in_comp = item.get_input_compression()
        in_comp_str = ""
        if in_comp == "gzip":
            in_comp_str = "zipped "

        out_comp = item.get_output_compression()
        out_comp_str = ""
        if out_comp == "as_input":
            out_comp_str = in_comp_str
        elif out_comp == "gzip":
            out_comp_str = "zipped "

        # file format labels
        in_format = self.item.get_input_format()
        in_format_str = ""
        if in_format in ("SAM", "BAM"):
            in_format_str = in_format
        elif in_format == "any":
            in_format_str = "SAM or BAM"

        out_format = self.item.get_output_format()
        out_format_str = ""
        if out_format == "as_input":
            out_format_str = in_format_str
        elif out_format in ("SAM", "BAM"):
            out_format_str = out_format
        elif out_format == "any":
            out_format_str = "SAM or BAM"

        # sort order labels
        in_sorting = self.item.get_input_sorting()
        in_sorting_str = ""
        if in_sorting in ("queryname", "coordinate"):
            in_sorting_str = " (sorted by %s)" % in_sorting
        elif in_sorting == "unsorted":
            in_sorting_str = " (%s)" % in_sorting

        out_sorting = self.item.get_output_sorting()
        out_sorting_str = ""
        if out_sorting == "as_input":
            out_sorting_str = in_sorting_str
        elif out_sorting in ("queryname", "coordinate"):
            out_sorting_str = " (sorted by %s)" % out_sorting
        elif in_sorting == "unsorted":
            out_sorting_str = " (%s)" % out_sorting

        io_format_str = ("Input:\t %s%s%s\n"
                         "Output:\t %s%s%s"
                         % (in_comp_str, in_format_str, in_sorting_str,
                            out_comp_str, out_format_str, out_sorting_str))
        io_format_lbl = QLabel(io_format_str)

        title_layout = QVBoxLayout()
#        title_layout.setMargin(0)
        title_layout.addWidget(title)
        title_layout.addWidget(description)
        title_layout.addWidget(io_format_lbl)

        title_frame = QWidget(self)
        title_frame.setLayout(title_layout)

        """
        Filter settings
        """
        self.settings = QWidget(self)
        self.settings.setEnabled(False)
        self.settings_layout = QFormLayout(self.settings)

        self.options = QWidget(self)
        self.options.setEnabled(False)
        self.options_layout = QFormLayout(self.options)

        self.toolbox = QTabWidget(self)
        self.toolbox.setEnabled(False)
        self.toolbox.addTab(self.settings, "Required")
        self.toolbox.addTab(self.options, "Optional")

        self.parameters = []
        for param in self.item.get_parameters():
            self.addParameter(param)

        icon = QIcon.fromTheme('view-filter')
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(icon.actualSize(QSize(32, 32))))

        """
        Put it all together
        """
        layout = QVBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(title_frame)
        layout.addWidget(self.toolbox)
        self.setLayout(layout)

    """ event handlers """

    def on_value_change(self, value):
        self.value_changed.emit("value in editor changed to %s" % value)

    """ Getters & Setters """

    def setName(self, name):
        self.name = name

    def addParameter(self, parameter):
        # import here to avoid circular imports!
        from samsifter.models.parameter import (FilterParameter,
                                                FilterThreshold,
                                                FilterSwitch,
                                                FilterFilepath)
        self.parameters.append(parameter)
        if isinstance(parameter, FilterThreshold):
            widget = SliderSpinboxCombo(self, parameter.getMinimum(),
                                        parameter.getMaximum(),
                                        parameter.getDefault(),
                                        parameter.getPrecision())
            widget.setValue(parameter.getValue())
            widget.setToolTip(parameter.getDesc())
            widget.spinner.valueChanged.connect(parameter.setValue)
            widget.spinner.valueChanged.connect(self.on_value_change)
        elif isinstance(parameter, FilterSwitch):
            widget = OptionSwitcher(self, parameter.getOptions())
            widget.setCurrentIndex(parameter.getValue())
            widget.setToolTip(parameter.getDesc())
            widget.group.buttonClicked[int].connect(parameter.setValue)
            widget.group.buttonClicked[int].connect(self.on_value_change)
        elif isinstance(parameter, FilterFilepath):
            widget = FileChooser(self)
            widget.setFilename(parameter.getValue())
            widget.setToolTip(parameter.getDesc())
            # ensure immediate update for revalidation
            widget.lineedit.textChanged.connect(widget.setFilename)
            widget.lineedit.textChanged.connect(parameter.setValue)
            widget.lineedit.textChanged.connect(self.on_value_change)
        elif isinstance(parameter, FilterParameter):
            widget = QCheckBox(self)
            widget.setChecked(parameter.getValue())
            widget.setToolTip(parameter.getDesc())
            widget.toggled.connect(parameter.setValue)
            widget.toggled.connect(self.on_value_change)

        if parameter.isRequired():
            self.settings.setEnabled(True)
            self.toolbox.setEnabled(True)
            self.settings_layout.addRow(parameter.getFormText(), widget)
        else:
            self.options.setEnabled(True)
            self.toolbox.setEnabled(True)
            self.options_layout.addRow(parameter.getFormText(), widget)
        self.update()
