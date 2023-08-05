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
from pdsapi.utils import JSON_HEADER, getResponseAsJson


class Groups(Resource):
    '''
    classdocs
    '''

    RESOURCE_NAME = 'groups'

    def __init__(self, session, locust_args = None):
        super( Groups, self ).__init__(session, 'data/PdsAMGroup', locust_args = None)

    def meta_descriptor(self, instance):
        return {'metaType': 'answerModuleGroup', 'name': instance['name']}
            
    def find_by_group_id(self, group_id):
        return self.list(params={'groupId': group_id})
    
    def advertise(self, group_id, invitations):
        request = {'groupId': group_id, 'invitations': invitations}
        extra = self._build_extra_args()
        resp = self.session.post("%s/operation/advertiseGroup" % self.resource_endpoint,
                                 data=json.dumps(request), headers=JSON_HEADER, **extra)
        return getResponseAsJson(resp)
    
    def join(self, group_id):
        request = {'groupId': group_id}
        extra = self._build_extra_args()
        resp = self.session.post("%s/operation/joinGroup" % self.resource_endpoint,
                                 data=json.dumps(request), headers=JSON_HEADER, **extra)
        return getResponseAsJson(resp)
    
    def accept_invite(self, code):
        request = {'rsvpCode': code}
        extra = self._build_extra_args()
        resp = self.session.post("%s/operation/acceptInvite" % self.resource_endpoint,
                                 data=json.dumps(request), headers=JSON_HEADER, **extra)
        return getResponseAsJson(resp)
    
    def leave(self, group_id):
        request = {'groupId': group_id}
        extra = self._build_extra_args()
        resp = self.session.post("%s/operation/leaveGroup" % self.resource_endpoint,
                                 data=json.dumps(request), headers=JSON_HEADER, **extra)
        return getResponseAsJson(resp)
    
    @property
    def type(self):
        return 'Answer Module Group'    
