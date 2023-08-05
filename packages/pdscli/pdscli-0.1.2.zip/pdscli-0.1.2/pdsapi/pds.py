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
import json

from pdsapi.resource import Resource
from utils import getResponseAsJson, JSON_HEADER


class Pds(Resource):
    '''
    classdocs
    '''


    RESOURCE_NAME = 'queries'
    

    def __init__(self, session, locust_args = None):
        super( Pds, self ).__init__(session, 'data/PdsPds', locust_args)
        
    def extract_name(self, instance):
        return instance['pdsId']
    
    def get_current(self):
        # Get the one for our PDS (have to qualify in case we are the system user)
        pds_list = self.list({'pdsId': {'pds_substitution' : 'pds_currentPds'}})
        if len(pds_list) == 0:
            return None
        return pds_list[0]

    def assign_namespace(self, namespace):
        instance = {}
        instance['namespace'] = namespace
        resp = self.session.post("%s/operation/assignNamespace" % (self.resource_endpoint),
                                 data = json.dumps(instance),
                                 headers = JSON_HEADER)
        return getResponseAsJson(resp)

    def promote(self, meta_objects):
        resp = self.session.post("%s/operation/promote" % (self.resource_endpoint),
                                 data = json.dumps(meta_objects),
                                 headers = JSON_HEADER)
        return getResponseAsJson(resp)
