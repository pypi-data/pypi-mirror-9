#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Feb 12 10:55:54 2015

@author: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""

import os
from os.path import isfile, dirname, exists

""" Qt4 """
from PyQt4.QtCore import QObject

""" custom libraries """
from samsifter.models.parameter import FilterFilepath


class WorkflowValidator(QObject):
    def __init__(self, workflow, parent=None):
        super(WorkflowValidator, self).__init__(parent)
        self.workflow = workflow
        self.input_errors = []
        self.model_errors = []
        self.output_errors = []

    def validate(self):
        """
        Validate input, workflow model and output in this order.
        """
        # checks have to occur in this order to make sense of stream parameters
        self.validate_input()
        self.validate_model()
        self.validate_output()

        # only an error-free workflow is considered valid
        errors = self.input_errors + self.model_errors + self.output_errors
        self.workflow.set_valid(len(errors) == 0)

        # send signal about validity changes
        self.workflow.validity_changed.emit("\n".join(errors))

        return errors

    def validate_output(self):
        """
        Validate output file of workflow.
        """
        self.output_errors = []

        # assuming output as expected by MEGAN and SAM2RMA
        out_format = 'SAM'
        out_sorting = 'queryname'
        out_compr = 'any'

        outfile = self.workflow.getOutFilename()
        if outfile is None:
            self.output_errors.append("output: no filename given")
        else:
            outdir = dirname(outfile)
            if not (exists(outdir) and os.access(outdir, os.W_OK)):
                self.output_errors.append(
                    "output: directory missing or not writable"
                )
            if outfile.endswith(('.sam', '.SAM')):
                out_format = 'SAM'
                out_compr = 'uncompressed'
            elif outfile.endswith(('.sam.gz', '.SAM.GZ')):
                out_format = 'SAM'
                out_compr = 'gzip'
            elif outfile.endswith(('.bam', '.BAM')):
                out_format = 'BAM'
                out_compr = 'uncompressed'
            else:
                out_format = 'as_input'
                out_compr = 'as_input'
                out_sorting = 'as_input'

        # check compatibility with post-processing and MEGAN
        if self.stream_format != out_format:
            self.output_errors.append(
                "output: expecting %s format but receiving %s format"
                % (out_format, self.stream_format)
            )
        if self.stream_sorting != out_sorting:
            self.output_errors.append(
                "output: expecting %s sorting but receiving %s sorting"
                % (out_sorting, self.stream_sorting)
            )
        if self.stream_compr != out_compr:
            self.output_errors.append(
                "output: expecting %s format but receiving %s format"
                % (out_compr, self.stream_compr)
            )

        # only an error-free output file is considered valid
        self.workflow.set_outfile_valid(len(self.output_errors) == 0)

    def validate_input(self):
        """
        Validate input file of workflow.
        """
        self.input_errors = []

        # assuming normal input as produced by MALT default settings
        input_format = 'SAM'
        input_sorting = 'queryname'
        input_compr = 'gzip'

        # stream starts off identical to input but may change with each step
        self.stream_format = input_format
        self.stream_sorting = input_sorting
        self.stream_compr = input_compr

        infile = self.workflow.getInFilename()
        if infile is None:
            self.input_errors.append("input: no filename given")
            self.workflow.set_infile_valid(False)
        else:
            if not (isfile(infile) and os.access(infile, os.R_OK)):
                self.input_errors.append("input: file missing or not readable")
                self.workflow.set_infile_valid(False)
            if infile.endswith(('.sam', '.SAM')):
                self.stream_format = 'SAM'
                self.stream_compr = 'uncompressed'
                self.workflow.set_infile_valid(True)
            elif infile.endswith(('.sam.gz', '.SAM.GZ')):
                self.stream_format = 'SAM'
                self.stream_compr = 'gzip'
                self.workflow.set_infile_valid(True)
            elif infile.endswith(('.bam', '.BAM')):
                self.stream_format = 'BAM'
                self.stream_compr = 'uncompressed'
                self.workflow.set_infile_valid(True)
            else:
                self.input_errors.append("input: unsupported file format")
                self.workflow.set_infile_valid(False)
                self.stream_format = 'any'
                self.stream_compr = 'any'
                self.stream_sorting = 'any'

        # only an error-free input file is considered valid
        self.workflow.set_infile_valid(len(self.input_errors) == 0)

    def validate_model(self):
        """
        Validate workflow model.
        """
        self.model_errors = []

        # validate model
        model = self.workflow.getModel()
        for idx, item in enumerate(model.iterate_items(), 1):
            item.set_valid(True)
            exp_format = item.get_input_format()
            exp_sorting = item.get_input_sorting()
            exp_compr = item.get_input_compression()
            if self.stream_format != exp_format and exp_format != 'any':
                self.model_errors.append(
                    "step %i: expecting %s format but receiving %s format"
                    % (idx, exp_format, self.stream_format)
                )
                item.set_valid(False)
            if self.stream_sorting != exp_sorting and exp_sorting != 'any':
                self.model_errors.append(
                    "step %i: expecting %s sorting but receiving %s sorting"
                    % (idx, exp_sorting, self.stream_sorting)
                )
                item.set_valid(False)
            if self.stream_compr != exp_compr and exp_compr != 'any':
                self.model_errors.append(
                    "step %i: expecting %s format but receiving %s format"
                    % (idx, exp_compr, self.stream_compr)
                )
                item.set_valid(False)

            # validate parameters
            for param in item.get_parameters():
                if (
                    isinstance(param, FilterFilepath)
                    and param.isRequired()
                    and not (
                        isfile(param.getValue())
                        and os.access(param.getValue(), os.R_OK)
                    )
                ):
                    self.model_errors.append(
                        "step %i: required parameter %s either not existing "
                        "or not readable" % (idx, param)
                    )
                    item.set_valid(False)

            if item.get_output_format() != 'as_input':
                self.stream_format = item.get_output_format()
            if item.get_output_sorting() != 'as_input':
                self.stream_sorting = item.get_output_sorting()
            if item.get_output_compression() != 'as_input':
                self.stream_compr = item.get_output_compression()

        # initiate repaint of view to reflect validity changes in model
        model.dataChanged.emit(model.index(1), model.index(model.rowCount()))

    """ Getters & Setters """

    def get_input_errors(self):
        return "\n".join(self.input_errors)

    def get_output_errors(self):
        return "\n".join(self.output_errors)

    def get_model_errors(self):
        return "\n".join(self.model_errors)
