# -*- coding: utf-8 -*-
"""
Created on Tue Jan 13 16:49:20 2015

@author: aldehoff
"""
from samsifter.models.workflow import Workflow
from samsifter.models.parameter import (FilterParameter, FilterThreshold,
                                        FilterFilepath, FilterSwitch)
from samsifter.models.filter import FilterItem


def create_workflow():
    """
    Generate workflow for test purposes.
    """
    wf = Workflow()
    wf.setInFilename("/some/path/to/a/file.sam")
    for idx in range(5):
        fp = FilterParameter("parameter%i" % idx, "a pretty parameter")
        ft = FilterThreshold("threshold%i" % idx, "a thrifty threshold")
        ff = FilterFilepath("filepath%i" % idx, "a funky filepath")
        fs = FilterSwitch("switch%i" % idx, "a super switch")

        f = FilterItem("filter%i" % idx, "a fine filter")
        f.addParameter(fp)
        f.addParameter(ft)
        f.addParameter(ff)
        f.addParameter(fs)

        wf.getModel().insertItem(f)
    return wf
