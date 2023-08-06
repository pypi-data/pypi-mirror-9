#!/usr/bin/env python
""" Used to suppress or block a regularly-scheduled or daemonized job from
    running or signal it to suspend or suppress operations.

    Cletus_supp is highly opinionated about scheduling:
       - Sometimes schedules need to be suppressed or suspended - maybe to
         prevent concurrency problems when a backup is running, maybe to
         reduce the number of jobs running to help diagnose a problem, etc.
       - Most teams rely on commenting jobs out in cron, or killing them,
         or modifying their config to do this.  These approaches are
         error-prone and often don't work well at all.
       - What's needed is the ability to temporarily suppress a schedule.

    That's what this module does - in a way that makes it easy for the apps:
       - Every application gets a suppression directory.  It can be
            - Either explicitely provided
            - Or left to default to XDG config standard.  On linux this
              would be: /home/.config/<appname>/suppression
         If the directory does not exist it will be created.
       - Applications can be "suppressed" by just touching a file or otherwise
         writing a file in this dir that complies with the following
         naming convention.
       - Suppression file naming convention:
            - name-<name>.suppress
            - <name> can be used by the application to suppress specific
              configurations without requiring dedicated directories for each.
              For example, if an application supported 400 customer accounts,
              rather than create 400 dedicated suppression directories, they
              could share a single suppression directory and use the name to
              identify which is being suppressed.
            - name-all.suppress will suppress all names.
        - Applications can check to see if they are suppressed at the begining
          of their operations, or at checkpoints.  If they're suppressed they
          can do whatever is desired - shut down gracefully, sleep, etc.

    Example Usage Scenario:
       - Large application server runs a hundred processes for extracting,
         aggregating, loading, validating, analyzing, and maintaining data.
       - Most processes run as daemons polling for the next set of work, some
         are scheduled to run at specific times (such as backups).
       - In order to minimize the number of corrupted or partial files backed-up,
         the backup process as an initial step that creates a suppression file
         for some jobs, then sleeps for 15 minutes prior to the actual backup
         starting.   When the backup is complete it removes this file.
       - One of the jobs that is affected runs as a daemon, and gets a new
         file to process every 10 minutes.  Every minute it polls for this file,
         but before it polls it checks to see if it's suppressed.  If it is, then
         it sleeps for another minute instead.
       - Another of the jobs creates a report once a day and emails it to admins.
         This job first runs a routine to wait until it's not suspended.  It will
         just keep sleeping then checking every ten minutes until it is no longer
         suspended.

    To Dos:
       - Allow use of ZooKeeper & database as an alternative to the config
         directory.  This will better support distributed processing.
       - Add more key-value pairs to suppression file name in order to support:
            - suppression start times
            - suppression stop times
            - suppression durations
            - suppression count
            - identity of suppressor
       - Add a suppression-file editor feature to help apps read & write the
         files.

    See the file "LICENSE" for the full license governing use of this file.
    Copyright 2013, 2014 Ken Farmer
"""


import os
import errno
import glob
import logging

import appdirs



class NullHandler(logging.Handler):
    def emit(self, record):
        #print record
        pass


class SuppressCheck(object):
    """ Typical Usage:
           supp_check = mod.SuppressCheck(pgm_name)
           if supp_check.suppressed():
               print 'WARNING: filemover has been suppressed'
               sys.exit(0)
        Inputs
           - app_name   - Used to look up XDG config dir unless config_dir
                          is specifically provided.  Also used for suppress
                          file name if that is not provided.
           - log_name   - Defaults to '__main__'
           - config_dir - If not provided will use XDG dirctory with app_name.
                          Defaults to None.
        Raises
           - OSError if config_dir doesn't exist and cannot be
             created or accessed.
    """

    def __init__(self,
                 app_name,
                 log_name='__main__',
                 config_dir=None):
        # set up logging
        self.logger   = logging.getLogger('%s.cletus_supp' % log_name)
        # don't print to sys.stderr if no parent logger has been set up:
        #logging.getLogger(log_name).addHandler(logging.NullHandler())
        self.logger.debug('SuppressCheck starting now')

        self.app_name        = app_name
        if config_dir:
            self.config_dir  = os.path.join(config_dir, 'suppress')
            self.logger.debug('config_dir derrived from arg: %s' % self.config_dir)
        else:
            self.config_dir  = os.path.join(appdirs.user_config_dir(app_name), 'suppress')
            self.logger.debug('config_dir provided via user_config_dir: %s' % self.config_dir)

        try:
            os.makedirs(self.config_dir)
            self.logger.info('Suppression dir created successfully')
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                self.logger.critical('Unknown OSError on creating config dir')
                raise




    def suppressed(self, suppress_name=None):
        """ Determines from suppress_name whether or not that process is
            suppressed.  Returns True/False.
            - if suppress_name is provided, then it can be suppressed by either:
                - a suppress file of name-<suppress_name>.suppress
                - or a suppress file of name-all.suppress
            - if suppress is not provided, then it defaults to the app_name
        """
        self.names_suppressed = self._get_suppressed_names()
        self.logger.critical(','.join(self.names_suppressed))

        if suppress_name is None:
            suppress_name = self.app_name

        if 'name-all.suppress' in self.names_suppressed:
            self.logger.info('Process has been suppressed')
            return True
        else:
            full_suppress_name = 'name-%s.suppress' % suppress_name
            self.logger.info('full_suppress_name: %s' % full_suppress_name)
            self.logger.info('self.names_suppressed: ')
            self.logger.info(','.join(self.names_suppressed))
            if full_suppress_name in self.names_suppressed:
                self.logger.info('Process has been suppressed')
                return True
            else:
                self.logger.info('Process has NOT been suppressed')
                return False


    def _get_suppressed_names(self):
        raw_files   = glob.glob(os.path.join(self.config_dir, '*.*'))
        clean_files = []
        for one_file in raw_files:
            self.logger.info('checking file: %s' % one_file)
            if _valid_suppress_file(one_file):
                head, tail = os.path.split(one_file)
                clean_files.append(tail)
            else:
                self.logger.critical('invalid suppress file: %s' % one_file)
                raise ValueError
        return clean_files


def _valid_suppress_file(name):
    head, tail = os.path.split(name)
    file_name, file_extension = os.path.splitext(tail)
    if file_extension != '.suppress':
        return False
    elif not file_name.startswith('name-'):
        return False
    else:
        return True




