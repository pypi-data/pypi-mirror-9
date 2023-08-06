# -*- coding: utf-8 -*-
"""Widgets for the main component of the SamSifter GUI representing workflows.

.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
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
    """Representation of file output action in GUI.

    Provides a way to specify an output file for the workflow and set options
    for post-processing, eg. the compilation of statistics files and creation
    of an RMA file.
    """

    def __init__(self, parent=None):
        """Initialize new instance of OutputWidget.

        Parameters
        ----------
        parent : QWidget, optional
            Parent Qt4 widget this widget belongs to, defaults to None.
        """
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
        self.file_btn.pressed.connect(self.show_dialog)

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

    def show_dialog(self):
        """Opens OS-specific file selection dialog to specify output file."""
        dialog = QFileDialog()
        dialog.setDefaultSuffix('SAM files (*.sam)')
        fname = dialog.getSaveFileName(
            self, 'Save as', expanduser("~"),
            "SAM (*.sam);;zipped SAM (*.sam.gz);;BAM (*.bam)"
        )
        self.file_entry.setText(fname)

    def set_filename(self, filename):
        """Updates filename in text box.

        Retains current cursor position despite updates.

        Parameters
        ----------
        filename : str
            Writable path to an existing directory for the new output file.
        """
        cursor = self.file_entry.cursorPosition()
        self.file_entry.setText(filename)
        self.file_entry.setCursorPosition(cursor)

    def highlight(self, boolean=True):
        """Indicates errors or pending actions by changing background color.

        Parameters
        ----------
        boolean : bool
            Activate highlighting of errors, defaults to True.
        """
        css = "QLineEdit {background-color: #ffe08c;}"
        if boolean:
            self.file_entry.setStyleSheet(css)
        else:
            self.file_entry.setStyleSheet(None)


class InputWidget(QWidget):
    """Representation of file input action in GUI.

    Provides a way to specify the input file for the workflow.
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
        self.file_btn.pressed.connect(self.show_dialog)

        self.grid = QGridLayout(self)
        self.grid.addWidget(self.icon_label, 0, 0, 1, 1)
        self.grid.addWidget(self.label, 0, 1, 1, 1)
        self.grid.addWidget(self.file_entry, 0, 2, 1, 1)
        self.grid.addWidget(self.file_btn, 0, 3, 1, 1)
        self.setLayout(self.grid)

    def show_dialog(self):
        """Opens OS-specific file selection dialog to set the input file."""
        dialog = QFileDialog()
        dialog.setDefaultSuffix(
            'SAM/BAM (*.sam *.SAM *.sam.gz *.SAM.GZ *.bam *.BAM)'
        )
        fname = dialog.getOpenFileName(
            self, 'Open file', expanduser("~"),
            "SAM/BAM (*.sam *.SAM *.sam.gz *.SAM.GZ *.bam *.BAM);;"
            "SAM (*.sam *.SAM);;zipped SAM (*.sam.gz *.SAM.GZ);;"
            "BAM (*.bam *.BAM);;All files (*)"
        )
        self.file_entry.setText(fname)

    def set_filename(self, filename):
        """Update filename in text box.

        Retains current cursor position despite updates.

        Parameters
        ----------
        filename : str
            Readable path to an existing directory for the existing input file.
        """
        cursor = self.file_entry.cursorPosition()
        self.file_entry.setText(filename)
        self.file_entry.setCursorPosition(cursor)

    def highlight(self, boolean=True):
        """Indicates errors or pending actions by changing background color.

        Parameters
        ----------
        boolean : bool
            Activate highlighting of errors, defaults to True.
        """
        css = "QLineEdit {background-color: #ffe08c;}"
        if boolean:
            self.file_entry.setStyleSheet(css)
        else:
            self.file_entry.setStyleSheet(None)


class FilterWidget(QWidget):
    """Representation of a filter action in GUI.

    Shows name, description and input/output requirements for filter items.
    Further provides a simple way to edit settings for all parameters of a tool
    or filter. Parameters are divided between two tabs for a) required and b)
    optional parameters and the focus is set on the required parameters.
    """
    value_changed = pyqtSignal(str, name='value_changed')

    def __init__(self, item, parent=None):
        """Initialize a new widget for the given filter item.

        Parameters
        ----------
        item : FilterItem
            Filter item to be displayed.
        parent : QWidget, optional
            Parent Qt4 widget this widget belongs to, defaults to None.
        """
        super().__init__(parent)
        self.item = item

        self.setGeometry(QRect(10, 1, 381, 51))
        self.setObjectName("widget")

        """ Filter label and description """
        title = QLabel(self.item.text())
        title.setWordWrap(True)
        description = QLabel(self.item.get_description())
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

        """ Filter settings """
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
            self.add_parameter(param)

        icon = QIcon.fromTheme('view-filter')
        icon_label = QLabel()
        icon_label.setPixmap(icon.pixmap(icon.actualSize(QSize(32, 32))))

        """ Put it all together """
        layout = QVBoxLayout(self)
        layout.setMargin(0)
        layout.addWidget(title_frame)
        layout.addWidget(self.toolbox)
        self.setLayout(layout)

    """ Event Handlers """

    def on_value_change(self, value):
        """Handles changes to editor values by emitting another signal."""
        self.value_changed.emit("value in editor changed to %s" % value)

    """ Getters & Setters """

    def add_parameter(self, parameter):
        """Adds specific composite widget to the parameter form.

        Chooses the widget based on type of parameter and divides them between
        the required and the optional tab depending on parameter settings.

        Parameters
        ----------
        parameter : FilterParameter
            Filter parameter to be displayed.
        """
        # import here to avoid circular imports!
        from samsifter.models.parameter import (
            FilterParameter, FilterThreshold, FilterSwitch, FilterFilepath
        )

        self.parameters.append(parameter)
        if isinstance(parameter, FilterThreshold):
            widget = SliderSpinboxCombo(self, parameter.get_minimum(),
                                        parameter.get_maximum(),
                                        parameter.get_default(),
                                        parameter.get_precision())
            widget.set_value(parameter.get_value())
            widget.setToolTip(parameter.get_description())
            widget.spinner.valueChanged.connect(parameter.set_value)
            widget.spinner.valueChanged.connect(self.on_value_change)
        elif isinstance(parameter, FilterSwitch):
            widget = OptionSwitcher(self, parameter.get_options())
            widget.set_current_index(parameter.get_value())
            widget.setToolTip(parameter.get_description())
            widget.group.buttonClicked[int].connect(parameter.set_value)
            widget.group.buttonClicked[int].connect(self.on_value_change)
        elif isinstance(parameter, FilterFilepath):
            widget = FileChooser(self)
            widget.set_filename(parameter.get_value())
            widget.setToolTip(parameter.get_description())
            # ensure immediate update for revalidation
            widget.lineedit.textChanged.connect(widget.set_filename)
            widget.lineedit.textChanged.connect(parameter.set_value)
            widget.lineedit.textChanged.connect(self.on_value_change)
        elif isinstance(parameter, FilterParameter):
            widget = QCheckBox(self)
            widget.setChecked(parameter.get_value())
            widget.setToolTip(parameter.get_description())
            widget.toggled.connect(parameter.set_value)
            widget.toggled.connect(self.on_value_change)

        if parameter.is_required():
            self.settings.setEnabled(True)
            self.toolbox.setEnabled(True)
            self.settings_layout.addRow(parameter.get_form_text(), widget)
        else:
            self.options.setEnabled(True)
            self.toolbox.setEnabled(True)
            self.options_layout.addRow(parameter.get_form_text(), widget)
        self.update()
