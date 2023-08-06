#!/usr/bin/env python
""" Used to quickly and easily set up somewhat comprehensive logging.

    Cletus_log is highly opinionated about what constitutes good logging:
       - Logs must be formatted with date, module name, level and msg
         so they can be sorted, searched, or reported on.
       - Logs should be written to a local file system, and should be
         automatically rotated to avoid filling the file system.
       - Logs should be written to the console as well for easy
         interactive debugging.
       - Logs should be trivial to set up, have intelligent defaults,
         be easy to maintain consistency across multiple programs,
         and expose as little logging jargon as possible.

    Anything else is a distraction, is insufficient, or is a (possibly
    totally legimitate) edge case.

    So cletus_log's objective is to make it very easy for most apps to
    provide good logging.

    See the file "LICENSE" for the full license governing use of this file.
    Copyright 2013, 2014 Ken Farmer
"""

from __future__ import division

import os
import sys
import logging
import logging.handlers
import errno

import appdirs


class LogManager(object):

    def __init__(self,
                 app_name=None,
                 log_dir=None,
                 log_fn='main.log',
                 log_name='__main__',
                 log_file_size=100000,
                 log_count=10,
                 log_to_console=True,
                 log_to_file=True):

        self.app_name       = app_name
        self.log_name       = log_name
        self.formatter      = None
        self.log_adapter    = None
        self.logger         = logging.getLogger(log_name)
        self.log_dir        = log_dir
        self.log_fn         = log_fn
        self.log_count      = log_count
        self.log_file_size  = log_file_size

        self._create_log_formatter()

        if log_to_file:
            self._create_file_handler()

        if log_to_console:
            self._create_console_handler()

        #logging from this class isn't working
        #self.logger_sub     = logging.getLogger('%s.cletus_log' % log_name)
        #self.logger.debug('logger started, written to: %s' % self.log_dir)

        # Ensure all crashes get logged:
        sys.excepthook = self._excepthook



    def _create_log_formatter(self):
        """ Creates a formatter to ensure all records get the following format:
                <ascii time> : <name> : <level name> : <message>
            where
                <ascii time> - has a format of yyyy-mm-dd hh24:mm:ss
                <name>       - is the given module name
                <level name> - is one of DEBUG, INFO, WARNING, ERROR, CRITICAL
                <message>    - is whatever the user provided.
        """
        log_format      = '%(asctime)s : %(name)-12s : %(levelname)-8s : %(message)s'
        date_format     = '%Y-%m-%d %H.%M.%S'
        self.formatter  = logging.Formatter(log_format, date_format)



    def _create_console_handler(self):
        """ Adds a handler to send logs to the console (stdout).
        """
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        self.logger.addHandler(console_handler)



    def _create_file_handler(self):
        """ Adds a handler to send logs to a file.  This is a rotating file handler,
            so when files reach log_file_size they will get renamed and have a numeric
            suffix added.

            It will attempt to make this directory if it does not exist.
        """
        if not self.log_dir:
            if self.app_name:
                self.log_dir = appdirs.user_log_dir(self.app_name)
            else:
                print 'CRITICAL: cannot write logs to files without either log_dir or app_name'
                sys.exit(1)

        try:
            os.makedirs(self.log_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                self.logger.critical('Log directory creation failed.  Log dir: %s' % self.log_dir)
                raise

        log_fqfn = os.path.join(self.log_dir, self.log_fn)

        file_handler = logging.handlers.RotatingFileHandler(log_fqfn,
                                                            maxBytes=self.log_file_size,
                                                            backupCount=self.log_count)
        file_handler.setFormatter(self.formatter)
        self.logger.addHandler(file_handler)



    def _excepthook(self, *args):
        """ Capture uncaught exceptions, write details into logger, exit.
        """
        self.logger.critical('Uncaught exception - exiting now. ', exc_info=args)
        sys.exit(1)



