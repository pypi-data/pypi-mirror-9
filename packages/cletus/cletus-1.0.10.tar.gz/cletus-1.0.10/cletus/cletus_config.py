#!/usr/bin/env python
""" Used to manage access to config files.

    Cletus_config is highly opinionated about what constitutes good config
    management:
       - Config files should be kept within the xdg directory:
            - linux:  $HOME/.config/<app name>
       - But overrides to the location, for special runs, migrations,
         testing, etc are occasionally necessary.
       - The best format at present for config files is yaml.
       - Config file contents should be validated.
       - Arguments should override config items.
       - It's easier to reference config items as namespaces than
         dictionaries.

    The objective of cletus_config is to deliver on this optinions in a way
    that makes it easy for applications.

    See the file "LICENSE" for the full license governing use of this file.
    Copyright 2013, 2014 Ken Farmer
"""

# todo:
# 1. validate the validation schema, sigh, well at least a little
# 2. allow users to add args and override config with them
# 3. allow users to lookup environ variables and override config with them

from __future__ import division
import os
import sys

import argparse
import time
import logging
from pprint import pprint as pp

import yaml
import validictory as valid
import appdirs


class NullHandler(logging.Handler):
    def emit(self, record):
        #print record
        pass


class ConfigManager(object):

    def __init__(self,
                 config_schema=None,
                 log_name='__main__',
                 namespace_access=True):

        self.cm_namespace_access = namespace_access

        # set up logging:
        self.cm_logger   = logging.getLogger('%s.cletus_config' % log_name)
        # don't print to sys.stderr if no parent logger has been set up:
        # logging.getLogger(log_name).addHandler(logging.NullHandler())
        self.cm_logger.debug('ConfigManager starting now')

        self.cm_config_schema    = config_schema
        self.cm_config_fqfn      = None

        self.cm_config_file      = {}
        self.cm_config_env       = {}
        self.cm_config_namespace = {}
        self.cm_config_iterable  = {}
        self.cm_config_defaults  = {}
        self.cm_config           = {}

        # store an original copy of variable names to use to protect
        # from updating by bunch later on.
        self.cm_orig_dict_keys   = self.__dict__.keys()


    def _bunch(self):
        for key, val in self.cm_config.items():
            if key in self.cm_orig_dict_keys:
                raise ValueError, 'config key is a reserved value: %s' % key
            elif key in dir(ConfigManager):
                raise ValueError, 'config key is a reserved value: %s' % key
            else:
                self.__dict__[key] = val

    def _post_add_maintenance(self, config):
        clean_config = self._remove_null_overrides(config)
        self.cm_config.update(clean_config)

        self.log_level = self.cm_config.get('log_level', None)
        if self.cm_namespace_access:
            self._bunch()


    def _remove_null_overrides(self, dictname):
        working_dict = dict(dictname)
        for key in dictname:
            if dictname[key] is None and self.cm_config.get(key, None) is not None:
                working_dict.pop(key)
        return working_dict


    def add_file(self,
                 app_name=None,
                 config_dir=None,
                 config_fn=None,
                 config_fqfn=None):

        # figure out the config_fqfn:
        if config_fqfn:
            self.cm_config_fqfn = config_fqfn
            self.cm_logger.debug('using config_fqn: %s' % config_fqfn)
        elif config_dir and config_fn:
            self.cm_config_fqfn = os.path.join(config_dir, config_fn)
            self.cm_logger.debug('using config_dir & config_fn: %s' % config_fqfn)
        elif app_name and config_fn:
            self.cm_config_fqfn = os.path.join(appdirs.user_config_dir(app_name), config_fn)
            self.cm_logger.debug('using app_name & config_fn: %s' % config_fqfn)
        else:
            self.cm_logger.critical('Invalid combination of args.  Provide either config_fqfn, config_dir + config_fn, or app_name + config_fn')
            raise ValueError, 'invalid config args'

        if not os.path.isfile(self.cm_config_fqfn):
            self.cm_logger.critical('config file missing: %s' % self.cm_config_fqfn)
            raise IOError, 'config file missing, was expecting %s' % self.cm_config_fqfn

        self.cm_config_file = {}
        with open(self.cm_config_fqfn, 'r') as f:
            self.cm_config_file = yaml.safe_load(f)

        self._post_add_maintenance(self.cm_config_file)



    def add_env_vars(self, key_list=None, key_to_lower=False):
        assert key_to_lower in [True, False]
        self.cm_config_env = {}

        final_key_list = key_list or self._get_schema_keys()
        if not final_key_list:
            raise ValueError, 'add_env_vars called without key_list or cm_config_schema'

        # get list of tuples of environment variables
        env_list = os.environ.items()

        for env_tup in env_list:
            if env_tup[0] in final_key_list:
                if key_to_lower:
                    self.cm_config_env[env_tup[0].lower()] = env_tup[1]
                else:
                    self.cm_config_env[env_tup[0]] = env_tup[1]

        self._post_add_maintenance(self.cm_config_env)


    def _get_schema_keys(self):
        if self.cm_config_schema:
            keylist = [var.upper() for var in self.cm_config_schema['properties'].keys()]
            return keylist
        else:
            return []


    def add_namespace(self, args):
        self.cm_config_namespace = {}
        self.cm_config_namespace.update(vars(args))
        self._post_add_maintenance(self.cm_config_namespace)

    def add_iterable(self, user_iter):
        self.cm_config_iterable = {}
        self.cm_config_iterable.update(user_iter)
        self._post_add_maintenance(self.cm_config_iterable)

    def add_defaults(self, default_dict):
        """ Applies defaults to empty config items with the following limits:
            - only if they have a default field created within the schema
            - only if they are top-level items - no nested items
        """
        # first create dict with all needed defaults:
        for key in self.cm_config:
           if self.cm_config[key] is None and default_dict.get(key, None) is not None:
               self.cm_config_defaults[key] = default_dict[key]

        # next update the main config from it:
        self._post_add_maintenance(self.cm_config_defaults)



    def validate(self, config_type='config', schema=None):

        config_schema = schema or self.cm_config_schema

        config_types = {'config':           self.cm_config,
                        'config_file':      self.cm_config_file,
                        'config_env':       self.cm_config_env,
                        'config_namespace': self.cm_config_namespace,
                        'config_iterable':  self.cm_config_iterable}
        assert config_type in config_types

        if self.cm_config_schema:
            try:
                valid.validate(config_types[config_type], config_schema)
            except valid.FieldValidationError as e:
                self.cm_logger.critical('Config error on field %s' % e.fieldname)
                self.cm_logger.critical(e)
                raise ValueError, 'config error: %s' % e
            else:
                return True
        else:
            return False



