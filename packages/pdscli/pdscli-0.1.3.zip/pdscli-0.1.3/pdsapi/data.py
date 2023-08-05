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
from pdsapi.utils import getResponseAsJson, JSON_HEADER


class Data(Resource):
    '''
    classdocs
    '''

    def __init__(self, session, type_name, locust_args = None):
        super( Data, self ).__init__(session, 'data/%s' % type_name, locust_args)
        self.type_name = type_name
        
    def execute_query(self, query_name, query_params):
        extra = self._build_extra_args("%s/query/%s?[params]" % (self.resource_endpoint, query_name))
        resp = self.session.get("%s/query/%s" % (self.resource_endpoint, query_name), 
                                params = query_params, **extra)
        return getResponseAsJson(resp)

    def execute_anon_query(self, query, query_params):
        extra = self._build_extra_args("%s/query?[params]" % (self.resource_endpoint))
        resp = self.session.post("%s/query" % (self.resource_endpoint),
                                 data = query,
                                 params = query_params,
                                 headers = JSON_HEADER,
                                 **extra)
        return getResponseAsJson(resp)
            
    @property
    def type(self):
        return '%s instance' % self.type_name