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

class Types(Resource):
    '''
    classdocs
    '''

    RESOURCE_NAME = 'types'

    def __init__(self, session, locust_args = None):
        super( Types, self ).__init__(session, 'data/PdsType', locust_args)
            
    def meta_descriptor(self, instance):
        return {'metaType': 'type', 'name': instance['name']}
                
    @property
    def type(self):
        return 'Type'