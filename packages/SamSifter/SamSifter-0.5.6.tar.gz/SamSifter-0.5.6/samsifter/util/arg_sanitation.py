# -*- coding: utf-8 -*-
"""Methods for input sanitation during argument parsing.

.. moduleauthor:: Florian Aldehoff <faldehoff@student.uni-tuebingen.de>
"""
import argparse
import os.path


def check_pos_int(arg):
    """Check if argument is a positive Integer.

    Parameters
    ----------
    arg : str
        command line argument

    Returns
    -------
    int
        typed value of command line argument

    Raises
    ------
    ArgumentTypeError
        If value is negative.
    """
    try:
        value = int(arg)
    except ValueError as err:
        raise argparse.ArgumentTypeError(str(err))

    if value < 0:
        raise argparse.ArgumentTypeError("expected value >= 0, got value = %i"
                                         % (value,))

    return value


def check_pos_float(arg):
    """Check if argument is a positive Float.

    Parameters
    ----------
    arg : str
        command line argument

    Returns
    -------
    float
        typed value of command line argument

    Raises
    ------
    ArgumentTypeError
        If value is negative.
    """
    try:
        value = float(arg)
    except ValueError as err:
        raise argparse.ArgumentTypeError(str(err))

    if value < 0:
        raise argparse.ArgumentTypeError("expected value >= 0, got value = %f"
                                         % (value,))

    return value


def check_pos_float_max1(arg):
    """Check if argument is a positive Float between 0 and 1.

    Parameters
    ----------
    arg : str
        command line argument

    Returns
    -------
    float
        typed value of command line argument

    Raises
    ------
    ArgumentTypeError
        If value is negative or larger than 1.0.
    """
    try:
        value = float(arg)
    except ValueError as err:
        raise argparse.ArgumentTypeError(str(err))

    if value <= 0.0 or value > 1.0:
        raise argparse.ArgumentTypeError("expected 0.0 > value <= 1.0, got \
                                         value = %f" % (value,))

    return value


def check_pos_float_max100(arg):
    """Check if argument is a positive Float between 0 and 100.

    Parameters
    ----------
    arg : str
        command line argument

    Returns
    -------
    float
        typed value of command line argument

    Raises
    ------
    ArgumentTypeError
        If value is negative or larger than 100.0.
    """
    try:
        value = float(arg)
    except ValueError as err:
        raise argparse.ArgumentTypeError(str(err))

    if value <= 0.0 or value > 100.0:
        raise argparse.ArgumentTypeError("expected 0.0 > value <= 100.0, got \
                                         value = %f" % (value,))

    return value


def check_percent(arg):
    """Check if argument is a positive Float between 0 and 100.

    Note
    ----
    Use check_pos_float_max100() instead.
    """
    return check_pos_float_max100(arg)


def check_sam(arg):
    """Check if argument is a SAM file.

    Parameters
    ----------
    arg : str
        filepath
    Returns
    -------
    str
        filepath to SAM file

    Raises
    ------
    ArgumentTypeError
        If file does not exist or has no .sam file extension.
    """
    if not (os.path.isfile(arg)):
        raise argparse.ArgumentTypeError("no such file: %s" % (arg,))

    base, ext = os.path.splitext(arg)
    if ext.lower() not in (".sam", ):
        raise argparse.ArgumentTypeError("file must have a .sam extension")

    return arg


def check_csv(arg):
    """Check if argument is a CSV file.

    Parameters
    ----------
    arg : str
        filepath

    Returns
    -------
    str
        filepath to SAM file

    Raises
    ------
    ArgumentTypeError
        If file does not exist or has no .csv file extension.
    """
    if not (os.path.isfile(arg)):
        raise argparse.ArgumentTypeError("no such file: %s" % (arg,))

    base, ext = os.path.splitext(arg)
    if ext.lower() not in (".csv", ):
        raise argparse.ArgumentTypeError("file must have a .csv extension")

    return arg
