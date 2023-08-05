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
import csv
import json
import sys

from pdsapi.pds import Pds
from pdscli.commands.exceptions import CommandFailure


class ResourceCmdProcessor(object):
    
    def __init__(self, session, resource_info):
        self.session = session
        self.resource_info = resource_info
        self.resource_api = None
        
    @property
    def resource_name(self):
        return self.resource_info['name']
        
    @property
    def resource_class(self):
        return self.resource_info['class']
        
    @property
    def is_promotable(self):
        return self.resource_info['promote']
        
    @property
    def can_load(self):
        return self.resource_info['loadable']
        
    @property
    def can_upsert(self):
        return self.resource_info['upsert']
        
    @property
    def resource(self):
        if self.resource_api is None:
            self.resource_api = self.resource_class(self.session)
        return self.resource_api
    
    def _display_response(self, response, is_json=True):
        if is_json:
            json.dump(response, sys.stdout,  indent = 2)
        else:
            sys.stdout.write(response)
        sys.stdout.write('\n')
        
    @property
    def name(self):
        return self.resource_name
    
    @property
    def help_text(self):
        return 'Commands to manipulate %s.' % self.resource_name
    
    def _add_subparsers(self, driver, subparsers):
        # Create parser for the resource commands themselves, then a sub-parser under that
        parser = subparsers.add_parser(self.name, help=self.help_text, add_help = False)
        return driver.create_sub_parser(parser, 'Resource command help.')
        
    def configure_parser(self, driver, subparsers):
        # Get our sub-sub-parser and create parsers for each command...
        subparsers = self._add_subparsers(driver, subparsers)
        
        parser = subparsers.add_parser('list', help='List the selected resource instances.')
        parser.add_argument('--filter', help='Filter and/or options to use when fetching the list.')
        parser.add_argument('--fields', default='name,id',
                            help='Comma separated list of fields to display (by default name and id are displayed)')
        parser.set_defaults(func=self.list)

        parser = subparsers.add_parser('show', help='Show the named resource instance.')
        parser.add_argument('name', help='Name of the resource instance to show.')
        parser.set_defaults(func=self.show)

        if self.can_load:
            parser = subparsers.add_parser('load', help='Load resource definitions from given file.')
            parser.add_argument('file', type=argparse.FileType('r'),
                                     help='File containing JSON array of resources to be loaded.')
            parser.set_defaults(func=self.load)
        
        if self.is_promotable:
            parser = subparsers.add_parser('promote', help='Promote the given instance(s) to the system PDS.')
            parser.add_argument('name', help='Name of the resource instance to promote.')
            parser.set_defaults(func=self.promote)

        parser = subparsers.add_parser('delete', help='Delete the resource instance with the given id.')
        parser.add_argument('name', help='Name of the resource instance to delete.')
        parser.add_argument('--system', action='store_true', default=False,
                            help='Delete the resource from the system PDS (ignored for non-PDS resources).')
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

        # Figure out the fields we have and construct header rows
        divider = '-'
        field_names = []
        dividers = []
        fields = args.fields.split(',')
        for field in fields:
            field_names.append(field[0:1].capitalize() + field[1:])
            dividers.append(divider * len(field))
        data = [field_names, dividers]
            
        # Add rows for each returned object instance
        for instance in resp:
            field_values = []
            for field in fields:
                if field == 'name':
                    field_values.append(self.resource.extract_name(instance))
                elif field == 'id':
                    field_values.append(str(self.resource.extract_id(instance)))
                else:
                    try:
                        field_values.append(instance[field])
                    except KeyError:
                        field_values.append('<not found>')
            data.append(field_values)

        # Format into columnar output
        col_width = max(len(word) for row in data for word in row) + 2
        for row in data:
            self._display_response("".join(word.ljust(col_width) for word in row), is_json=False)
        
    def show(self, args):
        resp = self.resource.find_by_name(args.name)
        if len(resp) == 0:
            raise CommandFailure("No instance named %s was found." % args.name)
        self._display_response(resp)
        
    def load(self, args):
        rsrc_list = json.load(args.file)
        for instance in rsrc_list:
            if self.can_upsert:
                self.resource.create(instance)
            else:
                name = self.resource.extract_name(instance)
                existing = self.resource.find_by_name(name)
                if len(existing) == 0:
                    self.resource.create(instance)
                else:
                    _id = self.resource.extract_id(existing[0])
                    self.resource.update(_id, instance)
            name = self.resource.extract_name(instance)
            self._display_response('Loaded %s %s...' % (self.resource.type, name), is_json=False)
        
    def delete(self, args):
        # Check to see if the requested resource exists
        resp = self.resource.find_by_name(args.name)
        if len(resp) == 0:
            raise CommandFailure("No instance named %s was found." % args.name)
        
        # Are we doing a local deletion or a system one?
        instance = resp[0]
        name = self.resource.extract_name(instance)
        if self.is_promotable and args.system:
            delete = self.resource.meta_descriptor(instance)
            delete['op'] = 'delete'
            pds = Pds(self.session)
            pds.promote([delete])
        else:
            _id = self.resource.extract_id(instance)
            self.resource.delete(_id)
        self._display_response('Deleted %s %s...' % (self.resource.type, name), is_json=False)
        
    def promote(self, args):
        # Should we promote everything or just one target option
        if args.name == 'all':
            # Get all aritfacts we can see and sort them according to origin
            local = []
            resp = self.resource.list()
            for instance in resp:
                if instance['pds_pds'] != 'system':
                    local.append(instance)
            return self._promote(local)
        else:
            resp = self.resource.find_by_name(args.name)
            if len(resp) == 0:
                raise CommandFailure("No instance named %s was found." % args.name)
            return self._promote([resp[0]])
        
    def _promote(self, instance_list):
        meta_list = []
        for instance in instance_list:
            meta_list.append(self.resource.meta_descriptor(instance))
            name = self.resource.extract_name(instance)
            self._display_response('Promoting %s %s...' % (self.resource.type, name), is_json=False)
        pds = Pds(self.session)
        return pds.promote(meta_list)