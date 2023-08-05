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
import argparse
import sys

from requests.exceptions import RequestException

from pdsapi import Session
from pdscli.commands import ConfigCmdProcessor, DataCmdProcessor, CommandFailure, LoginCmdProcessor, get_resource_commands


def main():
    driver = create_clidriver()
    return driver.main()


def create_clidriver():
    return CliDriver(Session())


class HelpPrinter(object):
    
    def __init__(self, parser):
        self.parser = parser
        
    def __call__(self, args):
        self.parser.print_help()


class CliDriver(object):
    '''
    
    @author: sfitts
    '''

    NO_LOGIN_TYPES = [LoginCmdProcessor, ConfigCmdProcessor, HelpPrinter]

    def __init__(self, session):
        self.session = session
        self.login_processor = LoginCmdProcessor(session)
        self.config_processor = ConfigCmdProcessor(session, self.login_processor)
    
    def main(self, args=None, prog='pds'):
        """

        :param args: List of arguments, with the 'pds' removed.  For example,
            the command "pds types list --filter namespace=foo" will have an
            args list of ``['types', 'list', '--filter', 'namespace=foo']``.

        """
        if args is None:
            args = sys.argv[1:]
            prog = sys.argv[0]
        parser = self._create_parser(prog)
        parsed_args = parser.parse_args(args)
        
        # Initialize the session and run the command
        try:
            self._intialize_session(parsed_args)
            parsed_args.func(parsed_args)
        except RequestException as e:
            sys.stdout.write('%s\n' % e)
        except CommandFailure as e:
            sys.stdout.write('%s\n' % e)
            pass
    
    def _intialize_session(self, args):
        # Get our config and make sure the host is set properly
        config = self.config_processor.config
        setattr(args, '_config', config)
        self.session.set_config(config)
        if args.host is not None:
            self.session.set_host(args.host)
        
        # If we aren't going to explicitly authenticate, then do it implicitly
        cmd_type = None
        try: 
            cmd_type = type(args.func.__self__)
        except AttributeError:
            cmd_type = type(args.func)
        if not cmd_type in self.NO_LOGIN_TYPES:
            self.login_processor.login(self.session.host)
        
     
    def _create_parser(self, prog):
        # Create root parser and add global arguments
        parser = argparse.ArgumentParser(prog=prog, 
                                         description='Issue commands to a PDS installation.',
                                         add_help = False)
        parser.add_argument('--host', help='The PDS host.')
        subparsers = self.create_sub_parser(parser, 'command help')
        
        # Add common commands
        self.login_processor.configure_parser(subparsers)
        self.config_processor.configure_parser(self, subparsers)
                
        # Add the resource commands
        parser.add_argument_group()
        for cmd in get_resource_commands(self.session):
            cmd.configure_parser(self, subparsers)
            
        # Add command for manipulating user data
        data_cmd = DataCmdProcessor(self.session)
        data_cmd.configure_parser(self, subparsers)
                
        return parser
    
    def create_sub_parser(self, parent, help_text):
        subparsers = parent.add_subparsers(help=help_text)
        help_parser = subparsers.add_parser('help', 
                                            help='Print help for a given command or sub-command')
        help_parser.set_defaults(func=HelpPrinter(parent))
        return subparsers

if __name__ == '__main__':
    sys.exit(main())