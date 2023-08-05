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
from config import ConfigCmdProcessor
from data import DataCmdProcessor
from exceptions import CommandFailure
from jobs import JobsCmdProcessor
from login import LoginCmdProcessor
from modules import AnswerModuleCmdProcessor
from resource import ResourceCmdProcessor
from utils import DEV_CLIENT_ID, DEV_SCOPES, get_resource_commands