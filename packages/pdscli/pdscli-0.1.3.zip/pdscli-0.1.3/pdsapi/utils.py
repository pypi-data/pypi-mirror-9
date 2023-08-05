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
Created on Jul 19, 2014

@author: sfitts
'''

import requests
from requests.exceptions import HTTPError, RequestException


JSON_HEADER = {'content-type': 'application/json'}
FORM_HEADER = {'content-type': 'application/x-www-form-urlencoded'}


class ServerBusy(RequestException):
    """Authentication of the user's credentials failed."""


class AuthenticationError(RequestException):
    """Authentication of the user's credentials failed."""


class AuthorizationError(RequestException):
    """User is not authorized to perform request."""


def find_endpoint(session, ep_name):
    resp = session.get("%s/.well-known/services" % session.base_url)
    discovery = getResponseAsJson(resp)
    return discovery[ep_name]


def getResponseAsJson(resp):
    # Is this a locust response that the caller wants to process?
    if hasattr(resp, 'locust_request_meta'):
        return resp
    
    # We need to process this response, returning either JSON or an error
    if (resp.status_code != requests.codes.ok # @UndefinedVariable
            and resp.status_code != requests.codes.created # @UndefinedVariable
            and resp.status_code != requests.codes.accepted # @UndefinedVariable
            and resp.status_code != requests.codes.no_content): # @UndefinedVariable
        error_msg = None
        exception = HTTPError
        if resp.status_code == 429:
            exception  = ServerBusy
            error_msg = 'The system has insufficient resources to process your request at this time.  If this error persists contact the administrator of your PDS installation.'
        elif resp.content:
            try:
                # Get the JSON and see if it is one of our error messages
                error_msg = resp.json()
                if type(error_msg) is list and len(error_msg) == 1 and type(error_msg[0]) is dict:
                    elm = error_msg[0]
                    if 'message' in elm:
                        error_msg = elm['message']
                        
                # Is this an authorization problem
                if resp.status_code == 401:
                    exception = AuthorizationError
            except ValueError:
                error_msg = resp.text
                if resp.status_code == 401:
                    exception = AuthenticationError
        else:
            error_msg = 'Request failed with error code %s and reason %s' % (resp.status_code, 
                                                                             resp.reason)
        raise exception(error_msg, response=resp)
    
    if (not resp.content):
        return {}
    return resp.json()
            