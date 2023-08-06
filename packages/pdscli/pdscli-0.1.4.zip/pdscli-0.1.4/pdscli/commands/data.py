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
import getpass
import json
from pdsapi.data import Data
from pdscli.commands.utils import RAW_DATA_PWD_OPTION
import sys

from pdsapi.upload import Upload


class DataCmdProcessor(object):
    
    def __init__(self, session):
        self.session = session
        
    def _get_resource(self, args):
        return Data(self.session, args.type)
        
    def _display_response(self, response):
        json.dump(response, sys.stdout,  indent = 2)
        sys.stdout.write('\n')
        
    def configure_parser(self, driver, subparsers):
        # Create parser for the resource commands themselves, then a sub-parser under that
        parser = subparsers.add_parser('data', help='Manipulate data in user defined types', 
                                       add_help = False)
        subparsers = driver.create_sub_parser(parser, 'Data query command help.')

        parser = subparsers.add_parser('fetch', help='Query for and return the given type.')
        parser.add_argument('type', help='The type for which to fetch data.')
        parser.add_argument('--query', help='Name of query to use to fetch the data.')
        parser.add_argument('--filter', help='Filter and/or query parameters to use when fetching the data.')
        parser.add_argument('--elevate', action='store_true', default=False,
                            help='Elevates privileges to permit access to raw data.')
        parser.set_defaults(func=self.fetch)

        parser = subparsers.add_parser('load', help='Load data for the given type from the given file.')
        parser.add_argument('type', help='The type for which to load data.')
        parser.add_argument('file', type=argparse.FileType('r'),
                            help='File containing JSON array of data to be loaded.')
        parser.set_defaults(func=self.load)
        
        parser = subparsers.add_parser('bulkLoad', 
                                       help='Bulk load data for multiple PDS users from the given file.')
        parser.add_argument('file', type=argparse.FileType('r'),
                                 help='File containing data to be loaded.  Currently supported formats are CSV and JSON.')
        parser.set_defaults(func=self.bulk_load)
        
        parser = subparsers.add_parser('delete', help='Delete the data instance with the given id.')
        parser.add_argument('type', help='The type for which to fetch data.')
        parser.add_argument('id', help='ID of the instance to delete')
        parser.set_defaults(func=self.delete)
        
        parser = subparsers.add_parser('deleteAll', help='Delete all instances of the given type.')
        parser.add_argument('type', help='The type for which to fetch data.')
        parser.set_defaults(func=self.delete_all)

    def fetch(self, args):
        params = {}
        if args.filter is not None:
            params = dict(csv.reader([item], delimiter='=', quotechar="'").next() 
                 for item in csv.reader([args.filter], delimiter=',', quotechar="'").next())

        # Should we attempt to elevate
        if args.elevate:
            if not params.has_key(RAW_DATA_PWD_OPTION):
                params[RAW_DATA_PWD_OPTION] = getpass.getpass()

        # Is this a straight get or a query execution
        if args.query is None:
            resp = self._get_resource(args).list(params=params)
        else:
            resp = self._get_resource(args).execute_query(args.query, params)
        self._display_response(resp)
        
    def load(self, args):
        rsrc_list = json.load(args.file)
        self._get_resource(args).create(rsrc_list)
            
    def bulk_load(self, args):
        upload = Upload(self.session)
        upload.upload(args.file, '')
        pass
        
    def delete(self, args):
        self._get_resource(args).delete(args.id)
        
    def delete_all(self, args):
        self._get_resource(args).delete_all()