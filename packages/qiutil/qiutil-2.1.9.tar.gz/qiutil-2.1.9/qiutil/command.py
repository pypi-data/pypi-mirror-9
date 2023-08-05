"""Command helper functions."""

# Absolute import (the default in a future Python release) resolves
# the logging import as the Python standard logging module rather
# than qiutil.logging.
from __future__ import absolute_import
import os
import tempfile
from logging import (ERROR, DEBUG)
from .logging import configure


def add_options(parser):
    """
    Adds the standard ``--log``, ``--quiet``, ``--verbose`` and ``--debug``
    options to the given command line argugment parser.
    """
    parser.add_argument('-l', '--log', help='the log file', metavar='FILE')
    verbosity_grp = parser.add_mutually_exclusive_group()
    verbosity_grp.add_argument(
        '-q', '--quiet', help="only log error messages", dest='log_level',
        action='store_const', const=ERROR)
    verbosity_grp.add_argument(
        '-d', '--debug', help='log debug messages', dest='log_level',
        action='store_const', const=DEBUG)


def configure_log(app, opts):
    """
    Configures the logger.

    :param app: the application name
    :param opts: the following keyword options:
    :keyword log: the log file
    :keyword log_level: the log level
    """
    log_cfg = {}
    if 'log' in opts:
        log_file = os.path.abspath(opts.get('log'))
        log_cfg['filename'] = log_file
    if 'log_level' in opts:
        log_cfg['level'] = opts.get('log_level')
    configure(app, **log_cfg)
