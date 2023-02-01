from secret import CLIENT_ID, CLIENT_SECRET
from datetime import datetime
from requests_oauthlib import OAuth2Session
import json, os

well_known_info = ""

CLIENT_REDIRECT_URI = 'http://localhost:9090/callback'
SCOPES_TO_REQUEST = {'offline_access', 'ag1', 'ag2', 'ag3', 'eq1', 'files'}
WELL_KNOWN_URL = 'https://signin.johndeere.com/oauth2/aus78tnlaysMraFhC1t7/.well-known/oauth-authorization-server'
WELL_KNOWN_TOKEN_URL = 'https://signin.johndeere.com/oauth2/aus78tnlaysMraFhC1t7/v1/token'

__location__ = os.path.realpath(
  os.path.join(os.getcwd(), os.path.dirname(__file__)))

def token_saver(token): 
  print('in token saver')
  with open(os.path.join(__location__, 'token.json'), 'w') as outfile:
    json.dump(token, outfile, indent=2)

def get_token():
  with open(os.path.join(__location__, 'token.json')) as json_file:
    token = json.load(json_file)
    # Add expires_at if necessary
    if 'expiration' in token and not 'expires_at' in token:
      token['expires_at'] = datetime.fromisoformat(token['expiration']).timestamp()
    return token
