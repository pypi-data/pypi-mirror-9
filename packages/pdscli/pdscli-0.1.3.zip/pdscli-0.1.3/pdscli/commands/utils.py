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

from pdsapi.groups import Groups
from pdsapi.jobs import Jobs
from pdsapi.modules import Modules
from pdscli.commands.groups import AnswerModuleGroupCmdProcessor
from pdscli.commands.jobs import JobsCmdProcessor
from pdscli.commands.modules import AnswerModuleCmdProcessor
from pdscli.commands.resource import ResourceCmdProcessor


DEV_CLIENT_ID = 'development_tools'
DEV_SCOPES = 'user developer'

ELEVATED_CLIENT_ID = 'elevated_dev_tools'
ELEVATED_SCOPES = 'user elevated'

ADMIN_CLIENT_ID = 'admin_tools'
ADMIN_SCOPES = 'admin'
RAW_DATA_PWD_OPTION = 'rawDataPassword'

def get_resource_commands(session):
    # Resources that have a special command processor
    cmd_override = {}
    cmd_override[Modules.RESOURCE_NAME] = AnswerModuleCmdProcessor
    cmd_override[Jobs.RESOURCE_NAME] = JobsCmdProcessor
    cmd_override[Groups.RESOURCE_NAME] = AnswerModuleGroupCmdProcessor
    
    cmd_list = []
    for entry in session.get_resources():
        name = entry['name']
        cmd_cls = cmd_override.get(name, ResourceCmdProcessor)
        cmd_list.append(cmd_cls(session, entry))
    return cmd_list
