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
import re

from pdsapi.data import Data
from pdscli.commands.exceptions import CommandFailure
from pdscli.commands.resource import ResourceCmdProcessor


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
        parser.set_defaults(func=self.show_execution_log)
        
        parser = subparsers.add_parser('run', help='Run the named module using the current user''s PDS.')
        parser.add_argument('name', help='The name of the module to run.')
        parser.set_defaults(func=self.run)
        
        parser = subparsers.add_parser('resetInputs', help="Reset the 'processed by' state for any streamed inputs.")
        parser.add_argument('name', help='The name of the module for which to reset the inputs.')
        parser.add_argument('--age', default=None,
                            help='Limits the reset to include documents created since the given <age>.'
                                 ' The format is <number> [millis | seconds | minutes | hours | days | weeks | months | years]')
        parser.add_argument('--system', action='store_true', default=False,
                            help='Perform the reset on the system definition of the answer module.')
        parser.set_defaults(func=self.reset)
        
        return subparsers

    def load(self, args):
        module = self.resource.upload(args.module_file, name=args.module_name, 
                                      schedule=args.schedule)
        self._display_response(module)
        
    def run(self, args):
        self.resource.run(args.name)
        
    def show_execution_log(self, args):
        # Get the log for the selected module
        module = self._get_module_by_name(args.name, args.system)
        exec_log = Data(self.session, 'PdsAMExecutionLog')
        for log_rec in exec_log.list({'moduleId': module['_id'], 'sort': '+startTime,+completionTime'}):
            self._display_response(log_rec)
            
    def reset(self, args):
        # Get the requested module
        module = self._get_module_by_name(args.name, args.system)
        
        # If we have an age argument, parse it
        qual = None
        if args.age is not None:
            offset = parse_time_offset(args.age)
            offset_int = int(offset['offset']) * -1
            offset['offset'] = offset_int
            qual = {'pds_createdAt': {'$gte': {'pds_substitution': {'pds_currentDateTimeOffset': offset}}}}
        
        self.resource.resetInputs(self.resource.extract_id(module), qual)
    
    def _get_module_by_name(self, name, system):
        params={'name': name}
        if system:
            params['pds_pds'] = 'system'
        module = self.resource.list(params=params)
        if len(module) == 0:
            raise CommandFailure("Could not find the module named %s" % name)
        
        # If we got more than one prefer the local over system
        if len(module) > 1:
            for m in module:
                if m['pds_pds'] != 'system':
                    module = m
                    break
        else:
            module = module[0]
        return module
        
def parse_time_offset(duration):
    """
    """
    if duration is None:
        return None
    match = re.match(r'(?P<offset>\d+)\s*(?P<units>millis|seconds|minutes|hours|days|weeks|months|years)', 
                      str(duration))
    if match is None:
        raise CommandFailure("'%s' is not a recognized duration." % duration)
    return match.groupdict()