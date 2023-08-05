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
import csv

from pdscli.commands.resource import ResourceCmdProcessor


class JobsCmdProcessor(ResourceCmdProcessor):
    
    def configure_parser(self, driver, subparsers):
        # Get our sub-sub-parser and create parsers for each command...
        subparsers = self._add_subparsers(driver, subparsers)
        
        parser = subparsers.add_parser('list', help='List the selected resource instances.')
        parser.add_argument('--filter', help='Filter and/or options to use when fetching the list.')
        parser.add_argument('--fields', default='id, moduleId',
                            help='Comma separated list of fields to display (by default name and id are displayed)')
        parser.set_defaults(func=self.list)

        parser = subparsers.add_parser('delete', help='Delete the resource instance with the given id.')
        parser.add_argument('id', help='Id of the resource instance to delete.')
        parser.set_defaults(func=self.delete)
        
        return subparsers

    def list(self, args):
        params = {}
        if args.filter is not None:
            params = dict(csv.reader([item], delimiter='=', quotechar="'").next() 
                 for item in csv.reader([args.filter], delimiter=',', quotechar="'").next())
            
        # By default, sort by name
        if not params.has_key('sort'):
            params['sort'] = self.resource.default_sort
        resp = self.resource.list(params=params)

        # Add rows for each returned object instance
        for instance in resp:
            self._display_response(instance)
        
        
