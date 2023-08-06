# -*- coding: utf-8 -*-
"""Abstraction of workflows with input, tool pipeline and output.

.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

import sys
import datetime
from os.path import basename, dirname
from os import getlogin


""" Qt4 """
from PyQt4.QtCore import (QObject, QFileInfo, pyqtSignal)

""" custom libraries """
from samsifter.gui.dialogs import BashOptions, RmaOptions
from samsifter.models.filter_model import FilterListModel
from samsifter.util.serialize import WorkflowSerializer
from samsifter.util.validation import WorkflowValidator
from samsifter.version import samsifter_version


class Workflow(QObject):
    """Container object for workflow related data.

    Takes care of serialization and validation using specialized objects.
    """

    # signals
    changed = pyqtSignal(str, name='changed')
    list_changed = pyqtSignal(str, name='list_changed')
    input_changed = pyqtSignal(str, name='input_changed')
    output_changed = pyqtSignal(str, name='output_changed')
    validity_changed = pyqtSignal(str, name='validity_changed')

    def __init__(self, parent=None):
        """Initializ a new instance of a workflow.

        Parameters
        ----------
        parent : QObject
            Parent Qt object, defaults to None.
        """
        super(Workflow, self).__init__(parent)
        self._filename = None
        self.in_filename = None
        self.out_filename = None
        self.run_compile_stats = True
        self.run_sam2rma = False

        self.model = FilterListModel(self)
        self.model.itemChanged.connect(self.on_change)
        self.model.rowsInserted.connect(self.on_insert)
        self.model.rowsRemoved.connect(self.on_remove)

        self.validator = WorkflowValidator(self)

        self._dirty = False     # no unsaved changes at this point
        self.infile_valid = False
        self.outfile_valid = False
        self.valid = False

    def commandline(self, hyphenated=False, multiline=False, batch=False,
                    basenames=False):
        """Creates Bash-compatible commandline for entire workflow.

        Parameters
        ----------
        hyphenated : bool, optional
            Enable hyphenation of entire commandline for use within variables
            evaluated by eval command; defaults to False.
        multiline : bool, optional
            Break long lines after each individual step of the workflow to
            improve readability; defaults to False.
        batch : bool, optional
            Enable use of variables that can be evaluated within code blocks
            like for loops or functions; defaults to False.
        basenames : bool, optional
            Shorten file paths to filename only; defaults to False.

        Returns
        -------
        str
            Commandline to be run in Bash or subprocess.
        """
        if self.model is None:
            return None

        # set hyphenation character(s)
        if hyphenated:
            hyphen = "'"
        else:
            hyphen = ""

        # set newline character(s)
        if multiline:
            # use \ for bash line continuation to increase readability
            newline = hyphen + "\\\n" + hyphen
        else:
            newline = ""

        # set filenames
        if batch:
            input_str = "${input}"
            output_str = "${output}"
        else:
            if self.in_filename is None:
                input_str = "${input}"
            else:
                if basenames:
                    input_str = basename(self.in_filename)
                else:
                    input_str = self.in_filename

            if self.out_filename is None:
                output_str = "${output}"
            else:
                if basenames:
                    output_str = basename(self.out_filename)
                else:
                    output_str = self.out_filename

        cl = hyphen + "cat " + input_str + newline
        for item in self.model.iterate_items():
            cl += " | " + item.commandline(basenames) + newline
        cl += " > " + output_str + hyphen + "\n"

        return cl

    def to_bash(self, filename,
                bash_options=BashOptions(),
                rma_options=RmaOptions()):
        """Write Bash script with optional batch processing capability.

        The batch variants take filenames as arguments while the standard call
        processes only the explicitly set input file.

        Parameters
        ----------
        filename : str
            Writable path of new bash script.
        bash_options : BashOptions, optional
            Bash options object, defaults to new instance.
        rma_options : RmaOptions, optional
            SAM2RMA options object, defaults to new instance.
        """
#        if bash_options is None:
#            bash_options = BashOptions()
#
#        if rma_options is None:
#            rma_options = RmaOptions()

        bash_params = ''
        if (
            bash_options.get_print_commands()
            and bash_options.get_stop_on_error()
        ):
            bash_params = ' -ex'
        elif bash_options.get_print_commands():
            bash_params = ' -x'
        elif bash_options.get_stop_on_error():
            bash_params = ' -e'

        bash_path = "/bin/bash"

        header = ("#!%s%s\n# SamSifter v%s workflow\n# created %s by %s\n\n"
                  % (bash_path, bash_params, samsifter_version,
                     datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
                     getlogin()))

        settings = (
            '# SAM2RMA settings\n'
            '#sam2rma_path="%s"\n'
            'sam2rma_path=`which sam2rma`\n'
            'top_percent="%.1f"\n'
            'min_score="%.1f"\n'
            'max_expected="%.2f"\n'
            'min_support_percent="%.3f"\n'
            '\n' % (rma_options.get_sam2rma_path(),
                    rma_options.get_top_percent(),
                    rma_options.get_min_score(),
                    rma_options.get_max_expected(),
                    rma_options.get_min_support_percent())
        )

        commando = "commando=%s\n" % self.commandline(
            hyphenated=True,
            multiline=True,
            batch=True,
            basenames=bash_options.get_use_basenames()
        )

        stats_switch = ""
#        if not bash_options.get_run_compile_stats():
#            stats_switch = "#"

        stats_command = (
            "compile_stats "
            "--prefix ${filename} "
            "--remove --verbose "
            "> ${dirname}/${filename}.sifted.csv 2>> ${log}")

        rma_switch = ""
#        if not bash_options.get_run_sam2rma():
#            rma_switch = "#"

        rma_command = (
            "${sam2rma_path} "
            "--minScore ${min_score} "
            "--maxExpected ${max_expected} "
            "--topPercent ${top_percent} "
            "--minSupportPercent ${min_support_percent} "
            "--in ${output} "
            "--out ${dirname} "
            "2>> ${log}"
        )

        function = (
            "# define individual job, requires filename as input\n"
            "job() {\n"
            "    %s"
            "    input=${1}\n"
            "    filename=`basename ${1}`\n"
            "    dirname=`pwd`\n"
            "    output=${filename}.sifted.sam\n"
            "    log=${filename}.sifted.log\n"
            "    eval ${commando} 2> ${log}\n"
            "    \n"
            "    # removal of temporary statistics files is optional\n"
            "    %s%s\n"
            "    # conversion into RMA files is optional\n"
            "    %s%s\n"
            "}\n"
            "# make function and variables available to subprocesses\n"
            "export -f job\n"
            "export sam2rma_path top_percent min_score max_expected min_support_percent\n"
            "\n" % (commando, stats_switch, stats_command, rma_switch,
                    rma_command)
        )

        standard_call = (
            "eval ${commando} 2> ${log}\n"
            "# removal of temporary statistics files is optional\n"
            "%s%s\n"
            "# conversion into RMA files is optional\n"
            "%s%s\n"
            "\n" % (stats_switch, stats_command, rma_switch, rma_command)
        )

        seq_call = (
            "# sequential execution, one after another\n"
            "for input in ${@}\n"
            "do\n"
            "    job ${input}\n"
            "done\n"
            "\n"
        )

        par_call = (
            "# parallel execution, one subshell per input file\n"
            "SHELL=$(type -p bash) parallel --gnu --progress job {} ::: ${@}\n"
            "\n"
        )

        summary = (
            "# create summary file for all processed files\n"
            "summarize_stats > samsifter.summary.csv\n"
            "\n"
        )

        footer = "exit\n"

        with open(filename, 'w') as f:
            # put the script together
            f.write(header)
            if bash_options.get_processing_mode() == BashOptions.SINGLE_MODE:
                f.write(settings)
                f.write(commando)
                if bash_options.get_use_basenames():
                    f.write('input="%s"\n' % basename(self.in_filename))
                    f.write('output="%s"\n' % basename(self.out_filename))
                    f.write('dirname=`pwd`\n')
                else:
                    f.write('input="%s"\n' % self.in_filename)
                    f.write('output="%s"\n' % self.out_filename)
                    f.write('dirname="%s"\n' % dirname(self.out_filename))
                f.write('filename=`basename ${input}`\n')
                f.write('log=${dirname}/${filename}.sifted.log\n')
                f.write(standard_call)
                # no summary here, compiled stats contain more information
            elif bash_options.get_processing_mode() == BashOptions.SEQUENTIAL_MODE:
                f.write(function)
                f.write(seq_call)
                f.write(summary)
            elif bash_options.get_processing_mode() == BashOptions.PARALLEL_MODE:
                f.write(settings)
                f.write(function)
                f.write(par_call)
                f.write(summary)
            f.write(footer)

    def clear(self):
        """Empties the workflow from all filenames and filter steps."""
        self.set_filename(None)
        self.set_in_filename(None)
        self.set_out_filename(None)
        self.model.removeAll()
        self.set_dirty()
        self.changed.emit("workflow cleared")

    def to_xml_string(self):
        """Represent workflow as XML tree.

        Returns
        -------
        str
            Pretty XML string representing entire workflow structure.
        """
        tree = WorkflowSerializer.workflow_to_xml(self)
        xml_string = WorkflowSerializer.tree_to_str(tree, pretty=True)
        return xml_string

    def __str__(self):
        """String representation of workflow.

        Returns
        -------
        str
            Hyphenated multiline commandline to run workflow.
        """
        return self.commandline(hyphenated=False, multiline=True)

    def __repr__(self):
        """Representation of workflow for debugging purposes."""
        rep = "SamSifter v%s Workflow" % samsifter_version
        rep += "\n- filename:\t\t%s" % self._filename
        rep += "\n- input:\t\t%s" % self.in_filename
        rep += "\n- output:\t\t%s" % self.out_filename
        rep += "\n- dirty:\t\t%s" % self._dirty
        rep += repr(self.model)
        rep += "\n"
        return rep

    """ Serialization """

    @staticmethod
    def formats():
        """Lists supported file formats for saving and loading.

        Returns
        -------
        list of str
            List of file extensions with leading asterisk, eg. ``*.ssx``.
        """
        return ["*.ssx", "*.SSX"]

    def save(self, filename=None):
        """Saves file and picks filetype depending on extension.

        Note
        ----
        Currently redundant as only XML output is supported since binary output
        was dropped.

        Parameters
        ----------
        filename : str, optional
            Writable path of new workflow file.

        Returns
        -------
        bool
            True if successful, otherwise False.
        str
            Error or success message.
        """
        if filename is not None:
            self._filename = filename

        if self._filename.endswith(".ssx") or self._filename.endswith(".SSX"):
            return self.save_xml()
        else:
            return (False,
                    "Failed to save %s: wrong file extension" % filename)

    def save_xml(self):
        """Save to file using XML serialization.

        Returns
        -------
        bool
            True if successful, otherwise False.
        str
            Error or success message.
        """
        error = None
        try:
            WorkflowSerializer.serialize(self, self._filename)
        except IOError as e:
            error = "input/ouptut error - failed to save: %s" % e
            print(error, file=sys.stderr)
        except OSError as e:
            error = "OS error - failed to save: %s" % e
            print(error, file=sys.stderr)
        finally:
            if error is not None:
                return False, error
            self._dirty = False
            return (True, "File saved to %s" % self._filename)

    def load(self, filename):
        """Load from file using XML deserialization.

        Parameters
        ----------
        filename : str, optional
            Readable path to existing workflow file.

        Returns
        -------
        bool
            True if successful, otherwise False.
        str
            Error or success message.
        """
        error = None
        try:
            WorkflowSerializer.deserialize(self, filename)
        except IOError as e:
            error = "input/output error - failed to load: %s" % e
            print(error, file=sys.stderr)
        except OSError as e:
            error = "OS error - failed to load: %s" % e
            print(error, file=sys.stderr)
        finally:
            if error is not None:
                return False, error
            self.input_changed.emit(self.in_filename)
            self.output_changed.emit(self.out_filename)
            self.set_filename(filename)
            self._dirty = False
            message = ("Loaded workflow with %i steps from %s"
                       % (self.model.rowCount(),
                          QFileInfo(filename).fileName()))
            self.changed.emit(message)
            return True, message

    """ event handlers """

    def on_change(self, item):
        """Handle change of workflow model."""
        self.validator.validate()
        self.validity_changed.emit("test of validity change signal")
        self.set_dirty(True)

    def on_insert(self, mdlidx, start, end):
        """Handle insertion of items into workflow model."""
        self.validator.validate()
        self.set_dirty(True)

    def on_remove(self, mdlidx, start, end):
        """Handle removal of items from workflow model."""
        self.validator.validate()
        self.set_dirty(True)

    """ Getters & Setters """

    def getModel(self):
        return self.model

#    def setModel(self, model):
#        self.model = model

    def get_in_filename(self):
        return self.in_filename

    def set_in_filename(self, filename):
        if filename == "":
            filename = None

        if self.in_filename != filename:
            self._dirty = True
            self.in_filename = filename
            self.validator.validate()
            self.input_changed.emit(filename)
            self.changed.emit("input filename changed to %s" % filename)

    def get_out_filename(self):
        return self.out_filename

    def set_out_filename(self, filename):
        if filename == "":
            filename = None

        if self.out_filename != filename:
            self._dirty = True
            self.out_filename = filename
            self.validator.validate()
            self.output_changed.emit(filename)
            self.changed.emit("output filename changed to %s" % filename)

    def get_run_compile_stats(self):
        return self.run_compile_stats

    def set_run_compile_stats(self, button_state):
        if int(button_state) == 0:
            self.run_compile_stats = False
        elif int(button_state) == 2:
            self.run_compile_stats = True

    def get_run_sam2rma(self):
        return self.run_sam2rma

    def set_run_sam2rma(self, button_state):
        if int(button_state) == 0:
            self.run_sam2rma = False
        elif int(button_state) == 2:
            self.run_sam2rma = True

    def is_dirty(self):
        return self._dirty

    def set_dirty(self, dirty=True):
        if self._dirty != dirty:
            self._dirty = dirty
            self.changed.emit("dirty flag changed to %s" % dirty)

    def is_valid(self):
        return self.valid

    def set_valid(self, valid=True):
        if self.valid != valid:
            self.valid = valid

    def infile_is_valid(self):
        return self.infile_valid

    def set_infile_valid(self, valid=True):
        if self.infile_valid != valid:
            self.infile_valid = valid

    def outfile_is_valid(self):
        return self.outfile_valid

    def set_outfile_valid(self, valid=True):
        if self.outfile_valid != valid:
            self.outfile_valid = valid

    def get_filename(self):
        return self._filename

    def set_filename(self, filename):
        if filename == "":
            filename = None

        if self._filename != filename:
            self._dirty = True
            self._filename = filename
            self.changed.emit("filename changed to %s" % filename)
