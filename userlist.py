#! /usr/bin/python
"""
A simple script demonstrating how to add new users and delete them.
Note that this isn't a great script to run on your production system,
but it will create a user unlikely to conflict with the ones you have.
This is more of sample code than anything else.


"""

import requests, logging, json
from random import randint
from akamai.edgegrid import EdgeGridAuth
from config import EdgeGridConfig
from urlparse import urljoin
import urllib
import os
from pprint import pprint
session = requests.Session()
debug = False
contractID="XXX-XXXX"

config = EdgeGridConfig({},"user")

# Enable debugging for the requests module
if debug:
  import httplib as http_client
  http_client.HTTPConnection.debuglevel = 1
  logging.basicConfig()
  logging.getLogger().setLevel(logging.DEBUG)
  requests_log = logging.getLogger("requests.packages.urllib3")
  requests_log.setLevel(logging.DEBUG)
  requests_log.propagate = True

# Set the config options
session.auth = EdgeGridAuth(
            client_token=config.client_token,
            client_secret=config.client_secret,
            access_token=config.access_token
)

if hasattr(config, 'headers'):
	session.headers.update(config.headers)

baseurl = '%s://%s/' % ('https', config.host)

def getResult(endpoint, parameters=None):
	if parameters:
		parameter_string = urllib.urlencode(parameters)
		path = ''.join([endpoint + '?',parameter_string])
	else:
		path = endpoint
	endpoint_result = session.get(urljoin(baseurl,path))
	if debug: print ">>>\n" + json.dumps(endpoint_result.json(), indent=2) + "\n<<<\n"
	return endpoint_result.json()

class BlankDict(dict):
        def __missing__(self, key):
            return ''
def getUsers():
	 print "======== USERS FOR CONTRACT "+contractID+"===="
	 user_url = '/user-admin/v1/accounts/'+contractID+'/users'
	 user_result = getResult(user_url)   
	 user_dump = json.dumps(user_result)
 	 ## Header
	 print	"Username;FirstName;LastName;Phone;Role;Group;Email;2faEnabled;2faConfigured;lastLogin"
	 for user in json.loads(user_dump, object_hook=BlankDict):
		username=user["username"]
		firstname = user["firstName"]
		lastname = user["lastName"]
		phone = user["phone"]
		contactId = user["contactId"]
		usertype = user["userType"]
		twofaEnabled = user["tfaEnabled"]
		twofaConfigured = user["tfaConfigured"]
		if user["lastLoginDate"]:
			lastlogin = user["lastLoginDate"]
		else:
			lastlogin = ""
		email = user["email"]
		for j in user["roleAssignments"]:
			role = j["roleName"]
			group = j["groupName"]
			print username,";",firstname,";",lastname,";",phone,";",role,";",group,";",email,";",twofaEnabled,";",twofaConfigured,";",lastlogin

if __name__ == "__main__":
	Id = {}
	getUsers()