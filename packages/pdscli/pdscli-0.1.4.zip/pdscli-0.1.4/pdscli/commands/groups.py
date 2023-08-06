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
import json

from pdsapi.modules import Modules
from pdscli.commands.exceptions import CommandFailure
from pdscli.commands.resource import ResourceCmdProcessor


class AnswerModuleGroupCmdProcessor(ResourceCmdProcessor):
    
    def configure_parser(self, driver, subparsers):
        # Get our sub-sub-parser and create parsers for each command...
        subparsers = self._add_subparsers(driver, subparsers)

        parser = subparsers.add_parser('list', help='List the groups associated with the given answer module.')
        parser.add_argument('module', help='The answer module whose groups we are listing.')
        parser.add_argument('--system', action='store_true', default=False,
                            help='Get the groups from the system version of the module (when more than one version exists).')
        parser.set_defaults(func=self.list)
        
        parser = subparsers.add_parser('show', help='Show the details of the given group.')
        parser.add_argument('groupId', help='The group id of the group being shown.')
        parser.set_defaults(func=self.show)
        
        parser = subparsers.add_parser('create', help='Create a group for the given answer module.')
        parser.add_argument('module', help='The answer module for which the group is being created.')
        parser.add_argument('name', help='The name of the group being created.')
        parser.add_argument('--join', action='store_true', default=False,
                            help='Indicates that the user creating the group should join as a member.')
        parser.add_argument('--system', action='store_true', default=False,
                            help='Associate the group with the system version of the module (when more than one version exists).')
        parser.set_defaults(func=self.create)
        
        parser = subparsers.add_parser('advertise', help='Invite one or more people to the named group.')
        parser.add_argument('groupId', help='The group id of the group to which we are inviting members.')
        parser.add_argument('invitations', type=argparse.FileType('r'),
                            help='File containing JSON array of the invitations to send.')
        parser.set_defaults(func=self.advertise)
        
        parser = subparsers.add_parser('join', help='Join a group to which you have been invited.')
        parser.add_argument('groupId', help='The group id of the group we are joining.')
        parser.set_defaults(func=self.join)
        
        parser = subparsers.add_parser('acceptInvite', help='Accept an invitation to join a group.')
        parser.add_argument('code', help='The invitation confirmation code.')
        parser.set_defaults(func=self.accept_invite)
        
        parser = subparsers.add_parser('leave', help='Leave a group of which we are currently a member.')
        parser.add_argument('groupId', help='The group id of the group we are leaving.')
        parser.set_defaults(func=self.leave)
        
        return subparsers

    def list(self, args):
        # Do list, filtering by module id
        module = self._get_module(args.module, args.system)     
        module_filter = 'answerModuleId=%s' % module['_id']
        setattr(args, 'filter', module_filter)
        setattr(args, 'fields', 'name,groupId')
        super( AnswerModuleGroupCmdProcessor, self ).list(args)
        
    def show(self, args):
        resp = self.resource.find_by_group_id(args.groupId)
        if len(resp) == 0:
            raise CommandFailure("No group with id %s was found." % args.groupId)
        self._display_response(resp)
        
    def create(self, args):
        module = self._get_module(args.module, args.system)     
        group = {'name': args.name, 'answerModuleId': module['_id']}
        if args.join:
            group['invitees'] = [{'type': 'user'}]
        group = self.resource.create(group)
        self._display_response('Created group with id %s...' % group['groupId'], is_json=False)

    def advertise(self, args):
        invitations = json.load(args.invitations)
        self.resource.advertise(args.groupId, invitations)
    
    def join(self, args):
        self.resource.join(args.groupId)
    
    def accept_invite(self, args):
        self.resource.accept_invite(args.code)
    
    def leave(self, args):
        self.resource.leave(args.groupId)
    
    def _get_module(self, module_name, is_system):
        # Get the module whose groups we want
        modules = Modules(self.session)
        params={'name': module_name}
        if is_system:
            params['pds_pds'] = 'system'
        module = modules.list(params=params)
        if len(module) == 0:
            raise CommandFailure('Did not find answer module %s.' % module_name)
        module = module[0]
        if module['type'] != 'shared':
            raise CommandFailure("The answer module %s is a '%s' module.  Only 'shared' modules may have groups." 
                                 % (module_name, module['type']))            
        return module