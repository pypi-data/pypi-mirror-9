# Copyright 2014 You Technology, Inc. or its affiliates. All Rights Reserved.
# 
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
# 
#     http://www.apache.org/licenses/LICENSE-2.0.html
# 
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.
from argparse import Namespace
'''
Created on Oct 30, 2014

@author: sfitts
'''
# Well known configuration sections

from ConfigParser import NoSectionError, NoOptionError
import ConfigParser
import os
import sys

from requests.exceptions import HTTPError

from pdsapi.pds import Pds
from pdsapi.users import Users
import pdscli
from pdscli.commands.exceptions import CommandFailure


GENERAL_SECTION = 'General'
SERVER_SECTION = 'Server' # deprecated

# Configuration options
HOST_OPT = 'host'
VERSION_OPT = 'version'
SECRET_OPT = 'secret'
ADMIN_SECRET_OPT = 'admin_secret'

USER_OPTIONS = {HOST_OPT, 'namespace', SECRET_OPT, ADMIN_SECRET_OPT}
HOST_OPTIONS = {SECRET_OPT, ADMIN_SECRET_OPT}


class ConfigCmdProcessor(object):
    
    def __init__(self, session, login_processor):
        self.session = session
        self.config = self.load_config()
        self.login_processor = login_processor
        
    def configure_parser(self, driver, subparsers):
        # Create parser for the configuration commands themselves, then a sub-parser under that
        parser = subparsers.add_parser('config', help='Configure PDS command line client.', 
                                       add_help = False)
        subparsers = driver.create_sub_parser(parser, 'Configuration command help.')
        
        parser = subparsers.add_parser('show', help='Show the current configuration values.')
        parser.set_defaults(func=self.show)

        parser = subparsers.add_parser('set', help='Set the named configuration value.')
        parser.add_argument('name', help='Name of the configuration value to set.')
        parser.add_argument('value', help='Value to set.')
        parser.set_defaults(func=self.set)

    def load_config(self):
        config_file= self._get_config_file()
        config_dir = os.path.dirname(config_file)
        if not os.path.exists(config_dir):
            os.makedirs(config_dir, mode=0755)
            config = self._default_config()
            self._update_config(config_file, config)
            return config
        
        config = ConfigParser.ConfigParser()
        config.read(config_file)
        self._upgrade_config(config_file, config)
        return config
    
    def _get_config_file(self):
        config_dir = os.path.expanduser('~/.youtech')
        return os.path.join(config_dir, 'config')

    def _default_config(self):
        config = ConfigParser.ConfigParser()
        config.add_section(GENERAL_SECTION)
        config.set(GENERAL_SECTION, HOST_OPT, 'pds.you.tc')
        config.set(GENERAL_SECTION, VERSION_OPT, pdscli.__version__)
        return config
    
    def show(self, args):
        # Display local settings
        self.config.write(sys.stdout)
        
        # Display PDS specific settings
        sys.stdout.write('\n[PDS]\n')
        try:
            pds = Pds(self.session)
            our_pds = pds.get_current()
            if our_pds is None:
                namespace = 'no value set'
                uploadPassword = 'no value set'
            else:
                namespace = our_pds.get('assignedNamespace', 'no value set')
                uploadPassword = 'no value set'
                if our_pds.has_key('uploadPassword'):
                    uploadPassword = 'value set'
                
            sys.stdout.write('namespace = %s\n' % namespace)
            sys.stdout.write('uploadPassword = %s\n' % uploadPassword)
        except HTTPError:
            sys.stdout.write('Unable to retrieve settings from your PDS.\n')
    
    def set(self, args):
        # Make sure the name is known
        if args.name not in USER_OPTIONS:
            raise CommandFailure("The configuration name '%s' is unknown.  Legal values are: %s" %
                                 (args.name, ', '.join(USER_OPTIONS)))
        config = self.config
        
        # Do the work
        if args.name == 'namespace':
            auth_info = self.login_processor.login(self.session.host)
            self._assign_namespace(args.value, auth_info)
            self.login_processor.logout(Namespace())
        elif args.name in HOST_OPTIONS:
            # Update configuration of the given host
            host = self.session.host
            if not config.has_section(host):
                config.add_section(host)
            config.set(host, args.name, args.value)
            self._update_config(self._get_config_file(), config)
        else:
            # Update general configuration
            config.set(GENERAL_SECTION, args.name, args.value)
            self._update_config(self._get_config_file(), config)
        
    def _assign_namespace(self, namespace, auth_info):
        pds = Pds(self.session)
        pds.assign_namespace(namespace)
        users = Users(self.session)
        cur_user = users.find_by_name(auth_info[0])[0]
        _id = cur_user.pop('id', None)
        cur_user.pop('sub', None)
        cur_user.pop('phone_number_verified', None)
        cur_user.pop('email_verified', None)
        cur_user['namespace'] = namespace
        users.update(_id, cur_user)
        
    def _update_config(self, config_file, config):
        with open(config_file, 'w') as fp:
            config.write(fp)
            
    def _upgrade_config(self, config_file, config):
        changed = False
        version = '0.1.1'
        if config.has_option(GENERAL_SECTION, VERSION_OPT):
            version = config.get(GENERAL_SECTION, VERSION_OPT)
        if version == '0.1.1':
            host = None
            try:
                config.add_section(GENERAL_SECTION)
                host = self._move_option(config, HOST_OPT, SERVER_SECTION, GENERAL_SECTION)
            except NoSectionError, NoOptionError:
                raise CommandFailure('The configuration file ~/.youtech/config is malformed.  Please remove before proceeding.')

            config.add_section(host)
            self._move_option(config, SECRET_OPT, SERVER_SECTION, host)
            self._move_option(config, ADMIN_SECRET_OPT, SERVER_SECTION, host)

            config.remove_section(SERVER_SECTION)
            version = '0.1.2'
            changed = True
    
        if version == '0.1.2':
            pass # current version
        
        # If anything changed update the version and re-write the file
        if changed:
            config.set(GENERAL_SECTION, VERSION_OPT, pdscli.__version__)
            self._update_config(config_file, config)
            
    def _move_option(self, config, option, old_section, new_section):
        value = None
        if config.has_option(old_section, option):
            value = config.get(old_section, option)
            config.set(new_section, option, value)
        return value
        