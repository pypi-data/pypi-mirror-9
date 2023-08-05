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
Created on Apr 25, 2014

@author: sfitts
"""

from requests.auth import HTTPBasicAuth, AuthBase

from utils import find_endpoint, getResponseAsJson

TOKEN_ENDPOINT = 'token_endpoint'

class OAuth2Bearer(AuthBase):
    """Attaches Bearer token to the given Request object."""
    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = "Bearer %s" % self.token
        return r

class OAuthClient(object):

    def __init__(self, session):
        
        self.session = session
        self.token_endpoint = find_endpoint(session, TOKEN_ENDPOINT)

    @property        
    def get_session(self):
        return self.session

    def password_grant(self, username, password, client_id, client_secret, scope = None):
        """
        Request an access token using the Password Grant type.

        :param username: string
        :param password: string
        :param client_id: string
        :param client_secret: string
        :param scope: string
        :return: JSON description of token
        """
        client_auth = HTTPBasicAuth(client_id, client_secret)
        data = {'grant_type': 'password',
                 'username': username,
                 'password': password,
                 'scope': scope
                 }
        resp = self.session.post(self.token_endpoint, data, auth=client_auth)
        return getResponseAsJson(resp)


    def client_grant(self, client_id, client_secret, scope = None):
        """
        Request an access token using the Client Grant type.

        :param client_id: string
        :param client_secret: string
        :param scope: string
        :return: JSON description of token
        """
        client_auth = HTTPBasicAuth(client_id, client_secret)
        data = {'grant_type': 'client_credentials',
                 'scope': scope
                 }
        resp = self.session.post(self.token_endpoint, data, auth=client_auth)
        return getResponseAsJson(resp)


    def refresh_token(self, refresh_token, client_id, client_secret):
        """
        Refresh an access token.

        :param refresh_token: string
        :param client_id: string
        :param client_secret: string
        :return: resulting HTTP response
        :rtype: JSON description of refreshed token
        """
        client_auth = HTTPBasicAuth(client_id, client_secret)
        data = {'grant_type': 'refresh_token',
                 'refresh_token': refresh_token
                 }
        resp = self.session.post(self.token_endpoint, data, auth=client_auth)
        return getResponseAsJson(resp)

    def revoke_token(self, access_token, client_id, client_secret):
        """
        Revoke an access token.

        :param access_token: string
        :param client_id: string
        :param client_secret: string
        :return: resulting HTTP response
        :rtype: JSON description of refreshed token
        """
        client_auth = HTTPBasicAuth(client_id, client_secret)
        token_url = "%s/%s" % (self.token_endpoint, access_token)
        resp = self.session.delete(token_url, auth=client_auth)
        return getResponseAsJson(resp)

    def expire_token(self, access_token, client_id, client_secret):
        """
        Expire an access token.

        :param access_token: string
        :param client_id: string
        :param client_secret: string
        :return: resulting HTTP response
        :rtype: JSON description of refreshed token
        """
        client_auth = HTTPBasicAuth(client_id, client_secret)
        token_url = "%s/%s?expire=true" % (self.token_endpoint, access_token)
        resp = self.session.delete(token_url, auth=client_auth)
        return getResponseAsJson(resp)

    def verify_token(self, access_token, client_id, client_secret):
        """
        Expire an access token.

        :param access_token: string
        :param client_id: string
        :param client_secret: string
        :return: resulting HTTP response
        :rtype: JSON description of refreshed token
        """
        client_auth = HTTPBasicAuth(client_id, client_secret)
        token_url = "%s/%s" % (self.token_endpoint, access_token)
        resp = self.session.get(token_url, auth=client_auth)
        return getResponseAsJson(resp)