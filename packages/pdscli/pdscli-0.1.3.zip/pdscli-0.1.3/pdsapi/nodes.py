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
from pdsapi.resource import Resource
from _io import UnsupportedOperation

class Nodes(Resource):
    '''
    classdocs
    '''

    RESOURCE_NAME = 'nodes'

    def __init__(self, session, locust_args = None):
        super( Nodes, self ).__init__(session, 'nodes', locust_args = None)
        
    def create(self, instance):
        raise UnsupportedOperation('Processing nodes are read-only.')

    def update(self, resource_id, instance):
        raise UnsupportedOperation('Processing nodes are read-only.')

    def delete(self, resource_id):
        raise UnsupportedOperation('Processing nodes are read-only.')
                
    def extract_id(self, instance):
        return instance['id']

    def extract_name(self, instance):
        return 'N/A'

    @property
    def default_sort(self):
        return '+id'
                
    @property
    def type(self):
        return 'Processing Node'