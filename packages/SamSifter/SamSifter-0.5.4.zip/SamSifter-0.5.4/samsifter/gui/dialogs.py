# -*- coding: utf-8 -*-
"""Dialogs to configure options for Bash script export and SAM2RMA.

This module also includes container objects for the specified options.

.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

""" Qt4 imports """
from PyQt4.QtGui import (
    QVBoxLayout, QCheckBox, QDialog, QDialogButtonBox, QLabel, QFormLayout,
    QRadioButton, QWidget, QButtonGroup
)
from PyQt4.QtCore import Qt

""" custom libraries """
from samsifter.gui.composites import SliderSpinboxCombo, FileChooser


class RmaOptionsDialog(QDialog):
    """Modal dialog to set SAM2RMA conversion settings."""
    def __init__(self, saved_options=None, parent=None):
        """Initialize a new modal RMA options dialog using current settings.

        Parameters
        ----------
        saved_options : RmaOptions, optional
            Currently saved SAM2RMA options, defaults to standard options if no
            previous settings exist.
        parent : QWidget, optional
            Parent Qt4 widget this widget belongs to, defaults to None.
        """
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
        self.sam2rma_path.set_filename(self.defaults.get_sam2rma_path())

        # override defaults with previous settings
        if self.options is not None:
            self.top_percent.set_value(self.options.get_top_percent())
            self.min_score.set_value(self.options.get_min_score())
            self.max_expected.set_value(self.options.get_max_expected())
            self.min_support_percent.set_value(
                self.options.get_min_support_percent()
            )
            self.sam2rma_path.set_filename(self.options.get_sam2rma_path())

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
        button_box.accepted.connect(self.save_options)

        layout = QVBoxLayout(self)
        layout.addWidget(form_box)
        layout.addWidget(button_box)
        self.setLayout(layout)

    def reset_form(self):
        """Resets all form elements to defaults."""
        self.top_percent.set_value(self.defaults.get_top_percent())
        self.min_score.set_value(self.defaults.get_min_score())
        self.max_expected.set_value(self.defaults.get_max_expected())
        self.min_support_percent.set_value(
            self.defaults.get_min_support_percent()
        )
        self.sam2rma_path.set_filename(self.defaults.get_sam2rma_path())

    def get_options(self):
        """Shows dialog and returns options unless user decides to cancel.

        Returns
        -------
        RmaOptions
            New SAM2RMA settings.
        """
        self.exec_()
        return self.options

    def save_options(self):
        """Stores current settings in BashOptions object to be returned.

        Closes the dialog when done.
        """
        self.options = RmaOptions()
        self.options.set_top_percent(self.top_percent.get_value())
        self.options.set_min_score(self.min_score.get_value())
        self.options.set_max_expected(self.max_expected.get_value())
        self.options.set_min_support_percent(
            self.min_support_percent.get_value()
        )
        self.options.set_sam2rma_path(self.sam2rma_path.get_filename())
        self.close()


class RmaOptions():
    """Options for the conversion of SAM to RMA files.

    Based on the command line arguments of SAM2RMA released with MEGAN 5.8.3.
    Sets default options as used by the Krause Lab in February 2015.
    """
    def __init__(
        self,
        sam2rma_path='/usr/local/megan/tools/sam2rma',
        top_percent=1,
        max_expected=0.01,
        min_score=50,
        min_support_percent=0.05,
        min_support=1
    ):
        """Initialize a new instance of SAM2RMA options.

        Parameters
        ----------
        sam2rma_path : str, optional
            Path to sam2rma executable, defaults to the standard path for
            system-wide installations of MEGAN on Linux in ``/usr/local``.
        top_percent : int, optional
            Threshold for the maximum percentage by which the score of a hit
            may fall below the best score achieved for a given read. Any hit
            that falls below this threshold is discarded. Defaults to 1%
            instead of 10%.
        max_expected : float, optional
            Maximum threshold for the expected value of hits. Any hit in the
            input data whose E-value exceeds this value is ignored. Defaults to
            0.01.
        min_score : int, optional
            Minimum threshold for the bit score of hits. Any hit in the input
            data that scores less than the given threshold is ignored. Defaults
            to 50.
        min_support_percent : float, optional
            Threshold for the minimum support that a taxon requires, as a
            percentage of assigned reads. This feature is turned off by setting
            the value to 0. Overrides the use of absolute thresholds with
            ``min_support``.
        min_support : int, optional
            Threshold for the minimum support that a taxon requires, that is,
            the number of reads that must be assigned to it so that it appears
            in the result. Any read that is assigned to a taxon that does not
            have the required support is pushed up the taxonomy until a node is
            found that has sufficient support. This value will be overridden by
            the relative ``min_support_percent`` if specified and not 0.
        """
        self.sam2rma_path = sam2rma_path
        self.top_percent = top_percent
        self.max_expected = max_expected
        self.min_score = min_score
        self.min_support_percent = min_support_percent
        self.min_support = min_support

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
    """Modal dialog to set Bash script export options.

    Switches between three types of processing modes and sets the Bash options
    to print executed commands and/or stop on errors.

    The available processing modes are:

    1. **Single Mode** processes only the specified input file and produces the
       specified output file similar to running the workflow in the GUI. This
       mode should be used with unmodified filenames unless all input files are
       located in the same directory as the exported bash script.

    2. **Sequential Mode** processes a list of arbitrary input files one file
       after another and saves the output to files renamed with the filename
       extension ``sifted``. This mode should be used with shortened filenames
       unless all of the required list files (CSV) are available at identical
       paths from all machines that this script is deployed to.

    3. **Parallel Mode** speeds up the process by distributing jobs across all
       available CPU cores and running them in parallel. This requires the
       installation of GNU ``parallel``. Similar to sequential mode above it
       should be used with shortened filenames unless all of the required list
       files (CSV) are available at identical paths from all machines that this
       script is deployed to.
    """

    def __init__(self, parent=None):
        """Initialize a new dialog to set Bash options.

        Parameters
        ----------
        parent : QWidget, optional
            Parent Qt4 widget this widget belongs to, defaults to None.
        """

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
        button_box.accepted.connect(self.save_options)

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

    def get_options(self):
        """Shows dialog and returns options unless user decides to cancel.

        Returns
        -------
        BashOptions
            New Bash export settings.
        """
        self.exec_()
        return self.options

    def save_options(self):
        """Stores current settings in BashOptions object to be returned.

        Closes the dialog when done.
        """
        self.options = BashOptions()
        self.options.set_processing_mode(self.mode.checkedId())
        self.options.set_use_basenames(self.basename_cb.isChecked())
        self.options.set_print_commands(self.print_cb.isChecked())
        self.options.set_stop_on_error(self.stop_cb.isChecked())
        self.close()


class BashOptions():
    """Options for the export of a workflow to a bash script."""
    SINGLE_MODE = 1         # one file only
    SEQUENTIAL_MODE = 2     # arbitrary files, uses Bash for-loop
    PARALLEL_MODE = 3       # arbitrary files, uses GNU parallel

    def __init__(self, use_basenames=True, processing_mode=PARALLEL_MODE,
                 print_commands=False, stop_on_error=True):

        """Initialize a new instance of Bash export options.

        Parameters
        ----------
        use_basename : bool, optional
            Shorten all paths to their filenames only, forcing the exported
            script to be located in the same directory as all of the required
            input files (eg. CSV filter lists). Defaults to True.
        processing_mode : int, optional
            Chooses one of three processing modes.

            1. Single Mode (one file only),
            2. Sequential Mode (arbitrary files, using Bash ``for``-loop), or
            3. Parallel Mode (arbitrary files, using GNU *parallel*)

            Defaults to 3.
        print_commands : bool, optional
            Enable the Bash option ``-x`` to print all executed commands.
            Defaults to False.
        stop_on_error : bool, optional
            Enable the Bash option ``-e`` to stop on errors. Defaults to True.
        """
        self.use_basenames = use_basenames
        self.processing_mode = processing_mode
        self.print_commands = print_commands
        self.stop_on_error = stop_on_error

    """ Getters & Setters """

    def set_processing_mode(self, mode=PARALLEL_MODE):
        self.processing_mode = mode

    def get_processing_mode(self):
        return self.processing_mode

    def set_use_basenames(self, boolean=False):
        self.use_basenames = boolean

    def get_use_basenames(self):
        return self.use_basenames

    def set_print_commands(self, boolean=True):
        self.print_commands = boolean

    def get_print_commands(self):
        return self.print_commands

    def set_stop_on_error(self, boolean=True):
        self.stop_on_error = boolean

    def get_stop_on_error(self):
        return self.stop_on_error
