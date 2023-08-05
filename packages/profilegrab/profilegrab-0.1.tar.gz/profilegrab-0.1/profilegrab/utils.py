"""
Module: utils.py
=====================

Description:
------------
        
    Contains some assorted utilities used in ProfileGrab

###############################
Charlie Hack
charlie@205consulting.com 
December 2014
###############################
"""
import settings


def print_status(stage, status, verbose=True):
    """
    prints status if verbose is set
    """
    if verbose:
        print "-----> %s: %s" % (stage, status)


def remove_nonascii(s):
    """
    Rip out annoying nonascii chars.
    Should really just use Python 3 ...
    """
    # assert isinstance(u, unicode), "{u} is not unicode, it is {type}".format(u=u, type=type(u))
    if isinstance(s, unicode):
        return s.translate(settings.nonascii_table)
    elif isinstance(s, str):
        return s.translate(None, settings.deletechars)
    else:
        raise TypeError("unrecognized type: {s} is {type}, not str or unicode".format(s=s, type=type(s)))

