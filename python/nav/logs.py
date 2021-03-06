# -*- coding: utf-8 -*-
#
# Copyright (C) 2006, 2007, 2009, 2011, 2012, 2014 UNINETT AS
#
# This file is part of Network Administration Visualized (NAV).
#
# NAV is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License version 2 as published by
# the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for
# more details.  You should have received a copy of the GNU General Public
# License along with NAV. If not, see <http://www.gnu.org/licenses/>.
#
"""NAV related logging functionality."""

import sys
import os
import logging
import ConfigParser
import nav.path

DEFAULT_LOG_FORMATTER = logging.Formatter('[%(asctime)s] [%(levelname)s] '
                                          '[%(name)s] %(message)s')
LOGGING_CONF_VAR = 'NAV_LOGGING_CONF'
LOGGING_CONF_FILE_DEFAULT = os.path.join(nav.path.sysconfdir, 'logging.conf')
_logger = logging.getLogger(__name__)


def set_log_levels():
    """
    Read the logging config file and set up log levels for the different
    loggers.
    """
    config = get_logging_conf()
    if 'levels' not in config.sections():
        return

    for logger_name in config.options('levels'):
        level = config.get('levels', logger_name)
        # Allow the config file to specify the root logger as 'root'
        if logger_name.lower() == 'root':
            logger_name = ''
        logger = logging.getLogger(logger_name)

        # Allow log levels to be specified as either names or values.
        # Translate any non-integer levels to integer first.
        if not level.isdigit():
            level = logging.getLevelName(level)
        try:
            level = int(level)
        except ValueError:
            # Default to INFO
            level = logging.INFO
        logger.setLevel(level)


def get_logging_conf():
    """
    Returns a ConfigParser with the logging configuration to use.

    Unless a specific config file is specified NAV_LOGGING_CONF environment
    variable, the default is to read from the file specified by
    LOGGING_CONF_FILE_DEFAULT .

    """
    filename = os.environ.get(LOGGING_CONF_VAR, LOGGING_CONF_FILE_DEFAULT)
    config = ConfigParser.ConfigParser()
    read = config.read(filename)
    if filename not in read and LOGGING_CONF_VAR in os.environ:
        _logger.error("cannot read logging config from %s, trying default %s",
                      filename, LOGGING_CONF_FILE_DEFAULT)
        config.read(LOGGING_CONF_FILE_DEFAULT)
    return config


def reset_log_levels(level=logging.WARNING):
    """Resets the log level of all loggers.

    The root logger's level is set to `level`, while other existing loggers in
    the hierarchy are reset to NOTSET.

    """
    root = logging.getLogger('')
    root.setLevel(level)
    all_loggers = root.manager.loggerDict.values()
    for logger in all_loggers:
        if hasattr(logger, 'setLevel'):
            logger.setLevel(logging.NOTSET)

def reopen_log_files():
    """
    Function to iterate over all FileHandlers in the logger hierarchy, close
    their streams and reopen them.
    """
    # Get the manager of the root logger
    root = logging.getLogger()
    manager = root.manager
    mylog = logging.getLogger('nav.logs')
    for logger in [root] + manager.loggerDict.values():
        try:
            for hdl in logger.handlers:
                if isinstance(hdl, logging.FileHandler):
                    mylog.debug("Reopening " + hdl.baseFilename)
                    hdl.flush()
                    hdl.acquire()
                    hdl.stream.close()
                    hdl.stream = open(hdl.baseFilename, hdl.mode)
                    hdl.release()
                    mylog.debug("Reopened " + hdl.baseFilename)
        except AttributeError:
            continue

def get_logfile_from_logger(logger=logging.root):
    """Return the file object of the first FileHandler of a given logger.

    This can be used as shorthand for redirecting the low-level stderr
    file descriptor to a log file after daemonization.

    Example usage:
        nav.daemon.daemonize('/var/run/nav/mydaemon.pid',
                             stderr=get_logfile_from_logger())

    Arguments:
        ``logger'' the logger object whose first FileHandler's file will be
                   returned.  If omitted, the root logger is searched for a
                   FileHandler.

    Returns:
        A file object, or None if no FileHandlers were found.

    """
    for handler in logger.handlers:
        if isinstance(handler, logging.FileHandler):
            return handler.stream


def init_stderr_logging(formatter=None):
    """Initializes logging to stderr.

    Log levels are read from logging.conf, the root logger's format is set to
    NAV's default format, and its handler is set to a StreamHandler writing
    to sys.stderr.

    """
    set_log_levels()

    handler = logging.StreamHandler(sys.stderr)
    formatter = formatter or DEFAULT_LOG_FORMATTER
    handler.setFormatter(formatter)
    root = logging.getLogger('')
    root.addHandler(handler)
