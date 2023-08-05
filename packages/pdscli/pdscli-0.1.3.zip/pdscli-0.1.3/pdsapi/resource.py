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
from utils import find_endpoint, getResponseAsJson, JSON_HEADER

import json

class Resource(object):
    '''
    Base class providing manipulation of all of the PDS resources.
    '''

    def __init__(self, session, resource, locust_args = None):
        api = find_endpoint(session, 'api_endpoint')

        self.session = session
        self.resource_endpoint = "%s/%s" % (api, resource)
        self.locust_args = locust_args
        
    def _build_extra_args(self, name = None):
        extra = {}
        if not self.locust_args is None:
            extra.update(self.locust_args)
            if not name is None:
                extra['name'] = name
        return extra
    
    def list(self, params=None):
        url = self.resource_endpoint
        if params is not None:
            params = '&'.join('{}={}'.format(key, val) for key, val in params.items())
            url = '%s?%s' % (url, params)
        extra = self._build_extra_args("%s?[params]" % self.resource_endpoint)
        resp = self.session.get(url, **extra)
        return getResponseAsJson(resp)
  
    def find_by_id(self, resource_id):
        extra = self._build_extra_args("%s/[id]" % self.resource_endpoint)
        resp = self.session.get("%s/%s" % (self.resource_endpoint, resource_id), **extra)
        return getResponseAsJson(resp)
    
    def find_by_name(self, name):
        return self.list(params={'name': name})
    
    def create(self, instance):
        extra = self._build_extra_args()
        resp = self.session.post(self.resource_endpoint, data=json.dumps(instance), 
                                 headers=JSON_HEADER, **extra)
        return getResponseAsJson(resp)

    def update(self, resource_id, instance):
        extra = self._build_extra_args("%s/[id]" % self.resource_endpoint)
        resp = self.session.put("%s/%s" % (self.resource_endpoint, resource_id), 
                                data=json.dumps(instance), headers=JSON_HEADER, **extra)
        return getResponseAsJson(resp)

    def delete(self, resource_id):
        extra = self._build_extra_args("%s/[id]" % self.resource_endpoint)
        resp = self.session.delete("%s/%s" % (self.resource_endpoint, resource_id), **extra)
        return getResponseAsJson(resp)
    
    def delete_all(self):
        extra = self._build_extra_args()
        resp = self.session.delete(self.resource_endpoint, **extra)
        return getResponseAsJson(resp)
    
    def extract_id(self, instance):
        return instance['_id']
    
    def extract_name(self, instance):
        return instance['name']
    
    def meta_descriptor(self, instance):
        return None
    
    @property
    def type(self):
        raise Exception('Must be overridden by specific resources.')
    
    @property
    def default_sort(self):
        return '+name'
