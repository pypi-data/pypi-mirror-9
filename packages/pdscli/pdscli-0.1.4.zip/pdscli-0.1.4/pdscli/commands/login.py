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

from ConfigParser import NoOptionError, NoSectionError
import getpass
from netrc import netrc
import os
import platform

from enum import Enum
from requests.exceptions import HTTPError

from pdsapi.oauth import OAuthClient
from pdsapi.profile import Profile
from pdsapi.users import Users
from pdsapi.utils import AuthenticationError, AuthorizationError
from pdscli.commands.config import ADMIN_SECRET_OPT
from pdscli.commands.exceptions import CommandFailure
from pdscli.commands.utils import DEV_CLIENT_ID, DEV_SCOPES, ELEVATED_SCOPES, \
    ADMIN_SCOPES, ELEVATED_CLIENT_ID, ADMIN_CLIENT_ID


class AuthorizationLevel(Enum):
    user = 1
    elevated = 2
    admin = 3

class LoginCmdProcessor(object):
    
    def __init__(self, session):
        self.session = session
        self.oauth = None
    
    def configure_parser(self, subparsers):
        parser = subparsers.add_parser('login', help='Authorize user with PDS.')
        parser.add_argument('--admin', action='store_true', default=False,
                            help='Authorize as PDS admin.')
        parser.add_argument('--elevated', action='store_true', default=False,
                            help='Authorize with elevated privilege level.')
        parser.set_defaults(func=self.login_cmd)
        
        parser = subparsers.add_parser('logout', help='Revoke any previous PDS authorization.')
        parser.set_defaults(func=self.logout)
        
        parser = subparsers.add_parser('expire', help="Expire the current user's token.")
        parser.set_defaults(func=self.expire)

    def login_cmd(self, args):
        create = True
        level = AuthorizationLevel.user
        if args.admin:
            create = False
            level = AuthorizationLevel.admin
        elif args.elevated:
            create = False
            level = AuthorizationLevel.elevated
        self.login(self.session.host, create_user=create, level=level)
        
    def logout(self, args):
        self.revoke_token(self.session.host)
        
    def expire(self, args):
        self.expire_token(self.session.host)
        
    def login(self, host, create_user=False, level=AuthorizationLevel.user):
        # Create an OAuth client if we need one
        if self.oauth is None:
            self.oauth = OAuthClient(self.session)
        
        # If this is a standard user login, load saved info    
        auth_info = None
        netrc_file, netrc_info = self._load_netrc()
        if level is AuthorizationLevel.user:
            auth_info = netrc_info.authenticators(host)
            
        # Do we have existing auth info or do we need to obtain it?
        if auth_info is None:
            # Check to see if should permit user creation
            if level is AuthorizationLevel.user and not create_user:
                raise CommandFailure("No user credentials found.  Use 'login' to establish identity.")
            
            # Get credentials from user and register
            username = raw_input('Email: ')
            password = getpass.getpass()
            
            # Determine client id, secret and scopes
            client_id = DEV_CLIENT_ID
            client_secret = self.session.client_secret
            scopes = DEV_SCOPES
            config = self.session.config
            if level is AuthorizationLevel.elevated:
                client_id = ELEVATED_CLIENT_ID
                client_secret = self.session.client_secret
                scopes = ELEVATED_SCOPES
            elif level is AuthorizationLevel.admin:
                try:
                    client_id = ADMIN_CLIENT_ID
                    client_secret = config.get(self.session.host, ADMIN_SECRET_OPT)
                    scopes = ADMIN_SCOPES
                except (NoSectionError, NoOptionError):
                    raise CommandFailure("To authorize with '%s' privileges you must first configure "
                                         "the appropriate client secret.  Contact the custodian of "
                                         "your PDS installation for this information." % level.name)

            # Authorize the user
            try: 
                token_info = self.oauth.password_grant(username, password, client_id, 
                                                       client_secret, scopes)
            except HTTPError as e1:
                if not create_user:
                    raise e1
                    
                # The likely cause here is that login failed, try creating the user
                try:
                    self.register_user(username, password)
                except HTTPError as e2:
                    if e2.response.status_code == 409:
                        # User exists, password is bad
                        raise CommandFailure('Failed to authenticate user credentials.')
                    raise e2
                
                # New user created, get token
                token_info = self.oauth.password_grant(username, password, client_id, 
                                                       client_secret, scopes)
            
            # Grab tokens from the response
            token = token_info['access_token']
            try:
                refresh = token_info['refresh_token']
            except KeyError:
                refresh = None
            auth_info = (username, refresh, token)

            # Update .netrc file so login is automatic from here on out
            netrc_info.hosts[host] = auth_info
            with open(netrc_file, 'w') as fp:
                self._write_netrc(netrc_info, fp)
                
        # Attempt to fetch profile (to prove creds are good)
        profile = Profile(self.session)
        profile_lst = None
        try:
            self.session.set_token(auth_info[2], auth_info[1])
            username = auth_info[0]
            profile_lst = profile.list(params={'email': username})
        except (AuthenticationError, AuthorizationError):
            try:
                auth_info = self._refresh_token(auth_info, host)
                username = auth_info[0]
                profile_lst = profile.list(params={'email': username})
            except HTTPError:
                raise CommandFailure('Existing credentials were invalid and have been removed.  Repeat command to reestablish identity.')

        # If we don't have a profile, create one, then return the auth info
        if len(profile_lst) == 0:
            profile.create({'email': auth_info[0]})
        return auth_info
    
    def _refresh_token(self, auth_info, host):
        # Refresh the token, get the new info and update the .netrc file
        netrc_file, netrc_info = self._load_netrc()
        token_info = None
        try:
            token_info = self.oauth.refresh_token(auth_info[1], DEV_CLIENT_ID, self.session.client_secret)
        except HTTPError as e:
            # Remove bogus token info and re-raise
            netrc_info.hosts.pop(host, None)
            with open(netrc_file, 'w') as fp:
                self._write_netrc(netrc_info, fp)
            raise e
         
        # Extract updated token info and update .netrc file
        token = token_info['access_token']
        refresh = token_info['refresh_token']
        auth_info = (auth_info[0], refresh, token)
        netrc_info.hosts[host] = auth_info
        with open(netrc_file, 'w') as fp:
            self._write_netrc(netrc_info, fp)
        return auth_info          

    def register_user(self, username, password):
        oauth_admin = self.oauth.client_grant('registration', 'bootstrap')
        self.session.set_token(oauth_admin['access_token'])
        users = Users(self.session)
        return users.create({'username': username, 'password': password, 'email': username})
    
    def revoke_token(self, host):
        # Create an OAuth client if we need one
        if self.oauth is None:
            self.oauth = OAuthClient(self.session)
        
        netrc_file, netrc_info = self._load_netrc()
        auth_info = netrc_info.authenticators(host)
        if not auth_info is None:
            # Revoke token as requested
            try:
                self.oauth.revoke_token(auth_info[2], DEV_CLIENT_ID, self.session.client_secret)
            except HTTPError as e:
                # Not found is OK since we're trying to nuke the token anyway
                if e.response.status_code != 404:
                    raise
                
            # Remove host information and rewrite netrc file
            netrc_info.hosts.pop(host, None)
            with open(netrc_file, 'w') as fp:
                self._write_netrc(netrc_info, fp)
    
    def expire_token(self, host):
        # Create an OAuth client if we need one
        if self.oauth is None:
            self.oauth = OAuthClient(self.session)
        
        netrc_file, netrc_info = self._load_netrc()
        auth_info = netrc_info.authenticators(host)
        if not auth_info is None:
            # Expire token as requested
            try:
                self.oauth.expire_token(auth_info[2], DEV_CLIENT_ID, self.session.client_secret)
            except HTTPError as e:
                # Should we take this seriously?
                if e.response.status_code != 404:
                    raise
                else:
                    # Token is bad, so just remove
                    netrc_info.hosts.pop(host, None)
                    with open(netrc_file, 'w') as fp:
                        self._write_netrc(netrc_info, fp)
    
    def _load_netrc(self):
        netrc_name = '~/.netrc'
        if platform.system() == 'Windows':
            netrc_name = '~/_netrc'
        netrc_file = os.path.expanduser(netrc_name)
        if not os.path.exists(netrc_file):
            open(netrc_file, 'w').close()
        netrc_info = netrc(netrc_file)
        return (netrc_file, netrc_info)
    
    def _write_netrc(self, netrc_info, fp):
        for host in netrc_info.hosts.keys():
            attrs = netrc_info.hosts[host]
            fp.write("machine %s\n" % host)
            fp.write("    login %s\n" % attrs[0])
            if attrs[1]:
                fp.write("    account %s\n" % attrs[1])
            fp.write("    password %s\n" % attrs[2])