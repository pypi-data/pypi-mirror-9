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
Created on Sep 18, 2014

@author: sfitts
'''
from pdsapi.resource import Resource

class Users(Resource):
    '''
    classdocs
    '''

    RESOURCE_NAME = 'users'

    def __init__(self, session, locust_args = None):
        super( Users, self ).__init__(session, 'users', locust_args)
        
    def find_by_name(self, name):
        return self.list(params={'username': name})
        
    def extract_id(self, instance):
        return instance['id']
    
    def extract_name(self, instance):
        return instance['username']

    @property
    def default_sort(self):
        return '+username'
                
    @property
    def type(self):
        return 'PDS User'