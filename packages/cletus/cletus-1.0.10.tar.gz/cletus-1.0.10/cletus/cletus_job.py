#!/usr/bin/env python
""" Used to ensure that only one job runs at a time.

    Cletus_job is highly opinionated about how to ensure only one job
    at a time runs, when that's important.
       - Applications should be able to wait for some amount of time for
         the older instance to complete.
       - Just checking on a pid in a file isn't enough: that pid might be
         orphaned, and you can easily get race conditions.
       - When a file system becomes full, a pidfile could be cataloged,
         but no pid can be written to it.  This needs to be handled.

    So cletus_job's objective is to make it extremely easy for most apps to
    handle this problem.

    See the file "LICENSE" for the full license governing use of this file.
    Copyright 2013, 2014 Ken Farmer
"""


import os
import errno
import time
import fcntl

import appdirs
import logging



class JobCheck(object):
    """ Ensures that only 1 job at a time runs.

    Typical Usage:
        job_check    = mod.JobCheck(pgm_name)
        if job_check.lock_pidfile():
            print 'Lock acquired, will start processing'
        else:
            print 'Try again later, already running'

        *** at end of program ***
        job_check.close()

    Inputs:
        app_name (str) - Used for two purposes: to lookup pid directory based on xdg
                         standards, and to name pid file.  Lookup only occurs if the
                         pid_dir is not provided.  Defaults to 'main'.
        log_name (str) - Should be passed from caller in order to ensure logging
                         characteristics are inherited correctly.  Defaults to __main__.
        pid_dir (str)  - Can be used instead of the automatic XDG directory
                         user_cache_dir, which is useful for testing among other things.
                         Defaults to None - which is fine as long as app_name is provided.

    Raises:
        ValueError   - Neither app_name nor pid_dir was provided, one must be
        OSError      - Could not create pid dir and it didn't already exist
    """

    def __init__(self,
                 app_name='main',
                 log_name='__main__',
                 pid_dir=None):

        self.logger   = logging.getLogger('%s.cletus_job' % log_name)
        # con't print to sys.stderr if no parent logger has been set up:
        #logging.getLogger(log_name).addHandler(logging.NullHandler())
        self.logger.debug('JobCheck starting now')

        # set up config/pidfile directory:
        self.app_name      = app_name
        self.pid_dir       = self._get_pid_dir(app_name, pid_dir)
        self.pid_fqfn      = os.path.join(self.pid_dir, '%s.pid' % self.app_name)

        self.new_pid       = os.getpid()
        self.start_time    = time.time()
        self.lock_acquired = False




    def lock_pidfile(self, wait_max=60):
        """
        Inputs:
           wait_max (int) - Maximum number of seconds for Jobcheck to keep retrying
                            lock acquisition.  If it exceeds this number it will
                            return False.
        Returns:
           True      - if lock was acquired
           False     - if lock was not acquired - pidfile is already locked
        Raises:
           IOError   - if pidfile is inaccessable
        """
        while not self._create_locked_pidfile(self.pid_fqfn, self.new_pid):
            if (time.time() - self.start_time) > wait_max:
                self.logger.error('wait_max exceeded, returning without lock')
                return False
            else:
                self.logger.warning('sleeping - waiting for lock')
                time.sleep(0.5)

        self.logger.debug('lock acquired - will return to caller')
        self.lock_acquired = True
        return True


    def _create_locked_pidfile(self, pid_fqfn, pid):
        """ Opens the pidfile, locks it, and writes the pid to it.
            Inputs:
                - pid_fqfn
                - pid
            Returns
                - True    - if locking was successful
                - False   - if locking was unsuccessful
            Raises
                - IOError - if file was inaccessible
        """
        try:
            self.pidfd = open(pid_fqfn, 'a')
        except IOError, e:
            self.logger.critical('Could not open pidfile: %s - permissions? missing dir?' % e)
            raise
        else:
            try:
                fcntl.flock(self.pidfd, fcntl.LOCK_EX|fcntl.LOCK_NB)
            except IOError:
                self.pidfd.close()
                return False
            else:
                self.pidfd.seek(0)
                self.pidfd.truncate()
                self.pidfd.write(str(pid))
                self.pidfd.flush()
                return True


    def _close_pidfile(self):
        """ Deletes pid from pidfile then closes it.
            Raises
                OSError if it cannot delete from pidfile or close it.
        """
        try:
            self.pidfd.seek(0)
            self.pidfd.truncate()
            self.pidfd.flush()
            self.pidfd.close()
        except OSError as e:
            if e.errno != errno.ENOENT:
                self.logger.critical('_delete_pidfile encountered IO error: %s' % e)
                raise


    def close(self):
        """ Final user interaction with class.
            Class can recover from prior jobs not doing this - but it's sloppy
            and could hypothetically result in errors.

        """
        if self.lock_acquired:
            self._close_pidfile()
        else:
            self.logger.warning('close() should not be called when lock was not acquired.  Will ignore.')



    def _get_pid_dir(self, app_name, arg_pid_dir):
        """Returns the pid_dir based on the arg_pid_dir if that's provided,
           otherwise by looking up the app_name in the xdg user_cache_dir.

           Inputs
                - app_name
                - arg_pid_dir 
           Returns
                - pid_dir
           Raises
                - ValueError - if neither app_name nor pid_dir is provided
                - OSError - if pid_dir doesn't exist and it can't make it
        """

        # first figure out what the directory is:
        if arg_pid_dir:
            pid_dir  = arg_pid_dir
            self.logger.debug('pid_dir will be based on arg: %s' % arg_pid_dir)
        else:
            if app_name:
                pid_dir  = os.path.join(appdirs.user_cache_dir(app_name), 'jobs')
                self.logger.debug('pid_dir will be based on user_cache_dir: %s' % pid_dir)
            else:
                err_msg = 'app_name must be provided if pid_dir is not'
                self.logger.critical(err_msg)
                raise ValueError, err_msg

        # next try to create it, just in case it isn't there
        try:
            os.makedirs(pid_dir)
        except OSError as exception:
            if exception.errno != errno.EEXIST:
                self.logger.critical('Error trying to create pid_dir: %s' % pid_dir)
                raise

        # finally, return it
        return pid_dir

