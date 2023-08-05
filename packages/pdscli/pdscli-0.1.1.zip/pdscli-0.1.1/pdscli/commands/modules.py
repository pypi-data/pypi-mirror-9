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
'''
Created on Oct 30, 2014

@author: sfitts
'''
import argparse

from pdsapi.data import Data
from pdscli.commands.resource import ResourceCmdProcessor
from pdscli.commands.exceptions import CommandFailure


class AnswerModuleCmdProcessor(ResourceCmdProcessor):
    
    def configure_parser(self, driver, subparsers):
        subparsers = super( AnswerModuleCmdProcessor, self ).configure_parser(driver, subparsers)
        
        parser = subparsers.add_parser('load', help='Load the given answer module file.')
        parser.add_argument('module_file', type=argparse.FileType('r'),
                            help='File containing the implementation of an answer module.')
        parser.add_argument('--module_name', 
                            help='The name of the module (by default this will be the name of the file without the extension.')
        parser.add_argument('--schedule', default='60m',
                            help='The frequency with which the answer module should be scheduled.')
        parser.set_defaults(func=self.load)
        
        parser = subparsers.add_parser('log', help='Display the execution log for the named module.')
        parser.add_argument('name', help='The name of the module for which to display the log.')
        parser.add_argument('--system', action='store_true', default=False,
                            help='Get the log for the system definition of the answer module.')
        parser.add_argument('--local', action='store_true', default=False,
                            help='Get the log for the local definition of the answer module.')
        parser.set_defaults(func=self.show_execution_log)
        
        parser = subparsers.add_parser('run', help='Run the named module using the current user''s PDS.')
        parser.add_argument('name', help='The name of the module to run.')
        parser.set_defaults(func=self.run)

        return subparsers

    def load(self, args):
        module = self.resource.upload(args.module_file, name=args.module_name, 
                                      schedule=args.schedule)
        self._display_response(module)
        
    def run(self, args):
        self.resource.run(args.name)
        
    def show_execution_log(self, args):
        params={'name': args.name}
        if args.system:
            params['pds_pds'] = 'system'
        module = self.resource.list(params=params)
        if len(module) == 0:
            raise CommandFailure("Could not find the module named %s" % args.name)
        
        # If we got more than one then see if we were asked to narrow it
        if len(module) > 1:
            if args.local:
                for m in module:
                    if m['pds_pds'] != 'system':
                        module = m
                        break
            else:
                raise CommandFailure("Found more than one copy of module %s.  Use --system or --local to disambiguate." % args.name)
        else:
            module = module[0]
        
        # Get the log for the selected module
        exec_log = Data(self.session, 'PdsAMExecutionLog')
        for log_rec in exec_log.list({'moduleId': module['_id'], 'sort': '+startTime,+completionTime'}):
            self._display_response(log_rec)