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

import os
from pdsapi.utils import find_endpoint

from utils import getResponseAsJson


class Upload(object):
    '''
    classdocs
    '''

    def __init__(self, session, locust_args = None):
        api = find_endpoint(session, 'api_endpoint')

        self.session = session
        self.resource_endpoint = "%s/upload" % api
        self.locust_args = locust_args

    def _build_extra_args(self, name = None):
        extra = {}
        if not self.locust_args is None:
            extra.update(self.locust_args)
            if not name is None:
                extra['name'] = name
        return extra
    
    def upload(self, fp, file_type = 'text/plain'):
        file_name = os.path.basename(fp.name)
        upload = [('deviceData', (os.path.basename(file_name), fp, file_type))]
        extra = self._build_extra_args()
        resp = self.session.post(self.resource_endpoint, 
                                 files = upload,
                                 **extra)
        return getResponseAsJson(resp)