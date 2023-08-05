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
from ConfigParser import NoOptionError, NoSectionError
from types import Types

import requests

from clients import Clients
from jobs import Jobs
from modules import Modules
from nodes import Nodes
from pdsapi.groups import Groups
from pdsapi.oauth import OAuth2Bearer
from pdscli.commands.config import GENERAL_SECTION, HOST_OPT, SECRET_OPT
from queries import Queries
from scopes import Scopes
from users import Users


class Session(requests.Session):
    '''
    @author: sfitts
   
    '''

    def __init__(self):
        super( Session, self ).__init__()
        
        # Default configuration
        self.config = None
        
        # Host on which the PDS installation is located (overrides configuration)
        self.host_override = None
        
    def set_config(self, config):
        self.config = config
        
    def get_host(self):
        if not self.host_override is None:
            return self.host_override
        return self.config.get(GENERAL_SECTION, HOST_OPT)
    
    def set_host(self, host):
        self.host_override = host
        
    host = property(get_host, set_host, None, 'The PDS installation host.')
    
    @property
    def base_url(self):
        return 'http://%s' % self.host
    
    @property
    def client_secret(self):
        try:
            secret = self.config.get(self.host, SECRET_OPT)
        except (NoSectionError, NoOptionError):
            secret = 'deadbeefcafe'
        return secret
    
    def set_token(self, token, refresh = None):
        self.auth = OAuth2Bearer(token)
        self.refresh_token = refresh
        
    def get_resources(self):
        return [
                {'name': Types.RESOURCE_NAME, 'class': Types, 'promote': True, 'upsert': True, 'loadable': True},
                {'name': Scopes.RESOURCE_NAME, 'class': Scopes, 'promote': True, 'upsert': True, 'loadable': True},
                {'name': Queries.RESOURCE_NAME, 'class': Queries, 'promote': True, 'upsert': True, 'loadable': True},
                {'name': Modules.RESOURCE_NAME, 'class': Modules, 'promote': True, 'upsert': True, 'loadable': True},
                {'name': Groups.RESOURCE_NAME, 'class': Groups, 'promote': False, 'upsert': True, 'loadable': False},
                {'name': Jobs.RESOURCE_NAME, 'class': Jobs, 'promote': False, 'upsert': False, 'loadable': False},
                {'name': Nodes.RESOURCE_NAME, 'class': Nodes, 'promote': False, 'upsert': False, 'loadable': False},
                {'name': Users.RESOURCE_NAME, 'class': Users, 'promote': False, 'upsert': False, 'loadable': True},
                {'name': Clients.RESOURCE_NAME, 'class': Clients, 'promote': False, 'upsert': False, 'loadable': True}
            ]