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
"""
PDSAPI
----
API for accessing services provided by the Personal Data Store.
"""
from pdsapi.oauth import OAuthClient, OAuth2Bearer
from session import Session
from users import Users
from types import Types
from scopes import Scopes
from queries import Queries
from modules import Modules
from profile import Profile
from pds import Pds
from groups import Groups