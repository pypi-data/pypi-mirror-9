#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec 16 20:09:30 2014

@author: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

import sys
import datetime
from os.path import basename, dirname
from os import getlogin


""" Qt4 """
from PyQt4.QtCore import (QObject, QFileInfo, pyqtSignal)

""" custom libraries """
from samsifter.gui.dialogs import BashOptions, RmaOptions
from samsifter.models.filter_model import SimpleFilterListModel
from samsifter.util.serialize import WorkflowSerializer
from samsifter.util.validation import WorkflowValidator
from samsifter.version import samsifter_version


class Workflow(QObject):
    """
    Container object for workflow related data.

    Takes care of serialization and validation using specialized objects.
    """
    MAGIC_NUMBER = 0x3051E
    FILE_VERSION = 100

    # signals
    changed = pyqtSignal(str, name='changed')
    list_changed = pyqtSignal(str, name='list_changed')
    input_changed = pyqtSignal(str, name='input_changed')
    output_changed = pyqtSignal(str, name='output_changed')
    validity_changed = pyqtSignal(str, name='validity_changed')

    def __init__(self, parent=None):
        super(Workflow, self).__init__(parent)
        self.filename = None
        self.in_filename = None
        self.out_filename = None
        self.run_compile_stats = True
        self.run_sam2rma = False

        self.model = SimpleFilterListModel(self)
        self.model.itemChanged.connect(self.on_change)
        self.model.rowsInserted.connect(self.on_insert)
        self.model.rowsRemoved.connect(self.on_remove)

        self.validator = WorkflowValidator(self)

        self._dirty = True
        self.infile_valid = False
        self.outfile_valid = False
        self.valid = False

    def commandline(self, hyphenated=False, multiline=False, batch=False,
                    basenames=False):
        """
        Create Bash-compatible commandline for entire workflow.

        Options:
        hyphenated          for use within variables for later evaluation
        multiline           as multiline string (for improved readability)
        batch               use variables for use within loop
        basenames           shorten file paths to filename only
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

    def toBash(self, filename,
               bash_options=BashOptions(),
               rma_options=RmaOptions()):
        """
        Write Bash script with optional batch processing capability.

        The batch variants take filenames as arguments while the standard call
        processes only the explicitly set input file.
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
        """
        Empties the workflow from all filenames and filter steps.
        """
        self.setFilename(None)
        self.setInFilename(None)
        self.setOutFilename(None)
        self.model.removeAll()
        self.setDirty()
        self.changed.emit("workflow cleared")

    def to_xml_string(self):
        """
        Represent workflow as XML tree.
        """
        tree = WorkflowSerializer.workflow_to_xml(self)
        xml_string = WorkflowSerializer.tree_to_str(tree, pretty=True)
        return xml_string

    def __str__(self):
        return self.commandline(False, True)

    def __repr__(self):
        rep = "SamSifter v%s Workflow" % samsifter_version
        rep += "\n- filename:\t\t%s" % self.filename
        rep += "\n- input:\t\t%s" % self.in_filename
        rep += "\n- output:\t\t%s" % self.out_filename
        rep += "\n- dirty:\t\t%s" % self._dirty
        rep += repr(self.model)
        rep += "\n"
        return rep

    """ Serialization """

    @staticmethod
    def formats():
        """
        Lists supported file formats for saving and loading.
        """
        return ["*.ssx", "*.SSX"]

    def save(self, filename=None):
        """
        Saves file and picks filetype depending on extension.
        """
        if filename is not None:
            self.filename = filename

        if self.filename.endswith(".ssx") or self.filename.endswith(".SSX"):
            return self.save_xml()
        else:
            return (False,
                    "Failed to save %s: wrong file extension" % filename)

    def save_xml(self):
        """
        Save to file using XML serialization.
        """
        error = None
        try:
            WorkflowSerializer.serialize(self, self.filename)
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
            return (True, "File saved to %s" % self.filename)

    def load(self, filename):
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
            self.setFilename(filename)
            self._dirty = False
            message = ("Loaded workflow with %i steps from %s"
                       % (self.model.rowCount(),
                          QFileInfo(filename).fileName()))
            self.changed.emit(message)
            return True, message

    """ event handlers """

    def on_change(self, item):
        self.validator.validate()
        self.validity_changed.emit("test of validity change signal")
        self.setDirty(True)

    def on_insert(self, mdlidx, start, end):
        self.validator.validate()
        self.setDirty(True)

    def on_remove(self, mdlidx, start, end):
        self.validator.validate()
        self.setDirty(True)

    """ Getters & Setters """

    def getModel(self):
        return self.model

#    def setModel(self, model):
#        self.model = model

    def getInFilename(self):
        return self.in_filename

    def setInFilename(self, filename):
        if filename == "":
            filename = None

        if self.in_filename != filename:
            self._dirty = True
            self.in_filename = filename
            self.validator.validate()
            self.input_changed.emit(filename)
            self.changed.emit("input filename changed to %s" % filename)

    def getOutFilename(self):
        return self.out_filename

    def setOutFilename(self, filename):
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

    def isDirty(self):
        return self._dirty

    def setDirty(self, dirty=True):
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

    def getFilename(self):
        return self.filename

    def setFilename(self, filename):
        if filename == "":
            filename = None

        if self.filename != filename:
            self._dirty = True
            self.filename = filename
            self.changed.emit("filename changed to %s" % filename)
