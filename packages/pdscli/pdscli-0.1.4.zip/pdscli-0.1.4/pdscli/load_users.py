# Copyright 2014 by You Technology, Inc.  All rights reserved.
from pdsapi.oauth import OAuthClient
from pdsapi.session import Session
from pdsapi.users import Users
import random
import string
import sys
from requests.exceptions import HTTPError

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print 'load_users <host> <email list>'
        sys.exit(1)
        
    host = sys.argv[1]
    file_name = sys.argv[2]
    print 'Loading users from %s into installation at %s' % (file_name, host)
    
    # Establish session and obtain oauth token
    session = Session()
    session.set_host(host)
    oauth = OAuthClient(session)
    oauth_admin = oauth.client_grant('registration', 'bootstrap')
    session.set_token(oauth_admin['access_token'])

    # Read the emails from the file and create a new user for each
    users = Users(session)
    with open(file_name) as f:
        for line in f:
            email = line.strip()
            password = ''.join(random.SystemRandom().choice(string.lowercase + string.uppercase + string.digits) for _ in xrange(10))
            try:
                users.create({'username': email, 'password': password, 'email': email})
                print 'Created user: %s' % email
            except HTTPError as e:
                print str(e)