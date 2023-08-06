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
import os

from pdsapi.pds import Pds
from pdsapi.resource import Resource
from pdsapi.utils import JSON_HEADER
from utils import getResponseAsJson


class Modules(Resource):
    '''
    classdocs
    '''

    RESOURCE_NAME = 'modules'

    def __init__(self, session, locust_args = None):
        super( Modules, self ).__init__(session, 'data/PdsAnswerModule', locust_args = None)

    def upload(self, fp, name = None, schedule = '60m'):
        file_name = os.path.basename(fp.name)
        if name is None:
            pds = Pds(self.session)
            our_pds = pds.get_current()
            name = os.path.basename(fp.name)
            name = os.path.splitext(name)[0]
            name = '%s.%s' % (our_pds['assignedNamespace'], name)
        form = {'moduleName': name, 'schedulingInterval': schedule}
        upload = [('answerModule', (os.path.basename(file_name), fp, 'text/plain'))]
        extra = self._build_extra_args()
        resp = self.session.post("%s/file" % self.resource_endpoint, 
                                 data = form, 
                                 files = upload,
                                 **extra)
        return getResponseAsJson(resp)
    
    def run(self, name):
        resp = self.session.get("%s/operation/execute?name=%s" % (self.resource_endpoint, name))
        return getResponseAsJson(resp)
    
    def resetInputs(self, moduleId, qual=None):
        extra = self._build_extra_args("%s/[id]" % self.resource_endpoint)
        request = {'moduleId': moduleId}
        if qual is not None:
            request['qual'] = qual
        resp = self.session.post("%s/operation/resetInputs" % self.resource_endpoint, 
                                data=json.dumps(request), headers=JSON_HEADER, **extra)
        return getResponseAsJson(resp)
  
    def meta_descriptor(self, instance):
        return {'metaType': 'answerModule', 'name': instance['name']}
            
    @property
    def type(self):
        return 'Answer Module'