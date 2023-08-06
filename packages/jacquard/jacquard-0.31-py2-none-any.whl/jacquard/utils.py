"""Functions and classes common to multiple modules.

"""
#By placing common functions here instead of in the jacquard module, we avoid
#circular dependencies. (e.g. jacquard depends on translate depends on jacquard)
from __future__ import absolute_import, print_function


#TODO (cgates): Why does this need a string? Seems like it should take a number?
def round_two_digits(val):
    try:
        if len(val.split(".")[1]) > 2:
            return "{0:.2f}".format(float(val))
    except IndexError:
        return val
    return val

class JQException(Exception):
    """Base class for all run-time exceptions in this module."""
    def __init__(self, msg, *args):
        #pylint: disable=star-args
        error_msg = msg.format(*[str(i) for i in args])
        super(JQException, self).__init__(error_msg)


class UsageError(JQException):
    """Raised for malformed command or invalid arguments."""
    def __init__(self, msg, *args):
        super(UsageError, self).__init__(msg, *args)

