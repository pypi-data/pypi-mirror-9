"""Logs messages to console and file.

Error, warning, info messages are written to console (stderr) and file.
Debug messages are written to file unless logger is initialized as verbose (in
which case debug is also echoed to console).
"""
#pylint: disable=invalid-name, global-statement
from __future__ import print_function, absolute_import
from datetime import datetime
import getpass
import logging
import os
import socket
import sys

WARNING_OCCURRED = False
"""Used to vary the Done message to emphasize upstream log warnings"""
log_filename = None


_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
_FILE_LOG_FORMAT = ('%(asctime)s|%(levelname)s|%(start_time)s|%(host)s|%(user)s'
                    '|%(tool)s|%(message)s')
_CONSOLE_LOG_FORMAT = '%(asctime)s|%(levelname)s|%(tool)s|%(message)s'
_logging_dict = {}
_verbose = False


def initialize_logger(command, verbose=False):
    """Sets command name and formatting for subsequent calls to logger"""
    global log_filename
    log_filename = os.path.join(os.getcwd(), "jacquard.log")
    logging.basicConfig(format=_FILE_LOG_FORMAT,
                        level="DEBUG",
                        datefmt=_DATE_FORMAT,
                        filename=log_filename)

    global _verbose
    _verbose = verbose

    start_time = datetime.now().strftime(_DATE_FORMAT)
    global _logging_dict
    _logging_dict = {'user': getpass.getuser(),
                     'host': socket.gethostname(),
                     'start_time': start_time,
                     'tool': command}

def error(message, *args):
    _print("ERROR", message, args)
    logging.error(_format(message, args), extra=_logging_dict)

def warning(message, *args):
    _print("WARNING", message, args)
    logging.warning(_format(message, args), extra=_logging_dict)
    global WARNING_OCCURRED
    WARNING_OCCURRED = True

def info(message, *args):
    _print("INFO", message, args)
    logging.info(_format(message, args), extra=_logging_dict)

def debug(message, *args):
    if _verbose:
        _print("DEBUG", message, args)
    logging.debug(_format(message, args), extra=_logging_dict)

def _print(level, message, args):
    now = datetime.now().strftime(_DATE_FORMAT)
    print(_CONSOLE_LOG_FORMAT % {'asctime': now,
                                 'levelname':level,
                                 'tool':_logging_dict['tool'],
                                 'message': _format(message, args)},
          file=sys.stderr)
    sys.stderr.flush()

def _format(message, args):
    try:
        log_message = message.format(*[str(i) for i in args])
    except IndexError as err:
        log_message = ("Malformed log message ({}: {})"
                       "|{}|{}").format(type(err).__name__,
                                        err,
                                        message,
                                        [str(i) for i in args])
    return log_message
