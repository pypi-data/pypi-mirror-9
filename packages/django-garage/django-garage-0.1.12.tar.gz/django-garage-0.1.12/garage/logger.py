# -*- coding: utf-8 -*-
"""
garage.logger

Logging for debug purposes.

HOW TO USE:

    # set the following in your Django project settings:
    LOG_DIR = os.path.join(SITE_ROOT, 'log')
    LOG_FILE = os.path.join(LOG_DIR, '%s.log' % server_acct)
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_PROJECT_CODE = server_acct

    # import "logger" and log debug messages with logger().debug():
    from garage.logger import logger
    logger().debug('this is a debug message')

* created: 2011-03-13 Kevin Chan <kefin@makedostudio.com>
* updated: 2014-11-21 kchan
"""

from __future__ import (absolute_import, unicode_literals)

import logging


# settings for debug log - add to project settings:

# LOG_DIR = os.path.join(SITE_ROOT, 'log')
# LOG_FILE = os.path.join(LOG_DIR, '%s.log' % server_acct)
# LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
# LOG_PROJECT_CODE = server_acct


# simple logger using Python logging module

log_levels = {
    'notset': logging.NOTSET,
    'debug': logging.DEBUG,
    'info': logging.INFO,
    'warning': logging.WARNING,
    'error': logging.ERROR,
    'critical': logging.CRITICAL
}

log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

def create_log(logname, logfile=None, level='debug', format=log_fmt):
    """
    Create and return simple file logger.

    * level is keyword in `log_levels` (`notset`, `debug`, `info`, etc.)
    * format is format of log entry to output

    :More info: `<http://docs.python.org/library/logging.html>`_

    :param logname: name of log.
    :param logfile: path of log file.
    :param level: log level (see ``log_levels``).
    :param format: log entry format (default is ``log_fmt``).
    :returns: logger object.
    """
    log_level = log_levels.get(level)
    logger = logging.getLogger(logname)
    logger.setLevel(log_level)
    if logfile:
        handler = logging.FileHandler(logfile)
    else:
        handler = logging.StreamHandler()
    handler.setLevel(log_level)
    handler.setFormatter(logging.Formatter(format))
    logger.addHandler(handler)
    return logger


# function to return a logging object for debug and diagnostic use

DebugLogger = None

def logger():
    """
    :return: simple logger object.
    """
    from garage import get_setting
    global DebugLogger
    if not DebugLogger:
        proj = get_setting('LOG_PROJECT_CODE')
        logfile = get_setting('LOG_FILE')
        logfmt = get_setting('LOG_FORMAT')
        DebugLogger = create_log(logname=proj, logfile=logfile, format=logfmt)
    return DebugLogger
