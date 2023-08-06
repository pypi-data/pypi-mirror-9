# -*- coding: utf-8 -*-

"""
do some crypto
"""

# Asymmetric key crypto
"""
from cryptography.fernet import Fernet

key = Fernet.generate_key()
f = Fernet(key)
token = f.encrypt('my deep dark secret')
print 'crypted token =', token
print f.decrypt(token)
"""


import hashlib
from hashlib import sha1
import json
import requests
import time


host = "https://tails.corp.dropbox.com"
client = "pynsot-dev"
clientVersion = "0.1"
clientDescription = 'test cilent for pynsot'
user = 'jathan'
get_authToken = lambda: str(int(time.time()))

cert = "n2phaq35gihfob3mfbtgyzpg4lgnf7xhuouilndk7ff3gvkzoaceorxdhgf5hc3uio2kvfidocgxrhz6pliee6bfl5nb3tiuilc3i25turx62ubnxpcngk7efd7gzgv2ilkz5v5h23b5qrcmzbysewj7jtstkrlw7xmdgdpco4ettatcnmaxw6whurtervl5bwotqqhoyoezdxduq37ph5erbkdo5qlm6o2rs7vu4w25hm25d6hfix2h5ckpcg7"

authToken = get_authToken()
def get_authSignature(authToken, cert):
    key = authToken + cert
    sig = sha1(key)
    return sig.hexdigest()

authSignature = get_authSignature(authToken, cert)
uri = '/api/conduit.connect'
url = host + uri

params = dict(
    client=client,
    clientVersion=clientVersion,
    clientDescription=clientDescription,
    user=user,
    host=host,
    authToken=authToken,
    authSignature=authSignature,
)

data = dict(
    params=json.dumps(params),
    output='json',
    __conduit__=True,
)

# Make the request to conduit.connect
r = requests.post(url, data=data)

# Parse the response (no error-handling yet)
result = r.json()['result']
conduit = {
    'sessionKey': result['sessionKey'],
    'connectionID': result['connectionID'],
}

# Good response:
"""
{u'error_code': None,
 u'error_info': None,
 u'result': {u'connectionID': 562985,
  u'sessionKey': u'wjnlt6wnpvcx2uajclrb3i5n4o3x3yzspim2uf7r',
  u'userPHID': u'PHID-USER-ugykvugfbmv4ijqlh5ln'}}
"""

# Bad response:
"""
{u'error_code': u'ERR-INVALID-USER',
 u'error_info': u'The username you are attempting to authenticate with is not valid.',
 u'result': None}
"""
