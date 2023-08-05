#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
methods for input sanitation during argument parsing

author: Florian Aldehoff <f.aldehoff@student.uni-tuebingen.de>
"""
import argparse
import os.path


def check_pos_int(arg):
    """ Check if argument is a positive Integer. """
    try:
        value = int(arg)
    except ValueError as err:
        raise argparse.ArgumentTypeError(str(err))

    if value < 0:
        raise argparse.ArgumentTypeError("expected value >= 0, got value = %i"
                                         % (value,))

    return value


def check_pos_float(arg):
    """ Check if argument is a positive Float. """
    try:
        value = float(arg)
    except ValueError as err:
        raise argparse.ArgumentTypeError(str(err))

    if value < 0:
        raise argparse.ArgumentTypeError("expected value >= 0, got value = %f"
                                         % (value,))

    return value


def check_pos_float_max1(arg):
    """ Check if argument is a positive Float between 0 and 1. """
    try:
        value = float(arg)
    except ValueError as err:
        raise argparse.ArgumentTypeError(str(err))

    if value <= 0.0 or value > 1.0:
        raise argparse.ArgumentTypeError("expected 0.0 > value <= 1.0, got \
                                         value = %f" % (value,))

    return value


def check_pos_float_max100(arg):
    """ Check if argument is a positive Float between 0 and 100. """
    try:
        value = float(arg)
    except ValueError as err:
        raise argparse.ArgumentTypeError(str(err))

    if value <= 0.0 or value > 100.0:
        raise argparse.ArgumentTypeError("expected 0.0 > value <= 100.0, got \
                                         value = %f" % (value,))

    return value


def check_percent(arg):
    """ Check if argument is a positive Float between 0 and 100. """
    return check_pos_float_max100(arg)


def check_sam(arg):
    """ Check if argument is a SAM file, """
    if not (os.path.isfile(arg)):
        raise argparse.ArgumentTypeError("no such file: %s" % (arg,))

    base, ext = os.path.splitext(arg)
    if ext.lower() not in (".sam", ):
        raise argparse.ArgumentTypeError("file must have a .sam extension")

    return arg


def check_csv(arg):
    """ Check if argument is a CSV file, """
    if not (os.path.isfile(arg)):
        raise argparse.ArgumentTypeError("no such file: %s" % (arg,))

    base, ext = os.path.splitext(arg)
    if ext.lower() not in (".csv", ):
        raise argparse.ArgumentTypeError("file must have a .csv extension")

    return arg
