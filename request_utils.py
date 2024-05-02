from secret import CLIENT_ID, CLIENT_SECRET
from auth import WELL_KNOWN_TOKEN_URL, get_token, token_saver
from db import get_tokens
from requests_oauthlib import OAuth2Session
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
import json

def get(protected_url):
  token = get_token()
  print('Getting ' + protected_url)
  client = OAuth2Session(CLIENT_ID, token=token, auto_refresh_url=WELL_KNOWN_TOKEN_URL,
    auto_refresh_kwargs={'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET}, token_updater=token_saver)
  response = client.get(protected_url, headers=MYJOHNDEERE_V3_JSON_HEADERS)
  if response.status_code != 200:
    print(f"Error calling JD API ({response.status_code}: {response.text})")
    return { 'status_code': response.status_code, 'text': response.text }
  else:
    return response.json()

def find_link(iterable, rel):
  link = next((link for link in iterable if link['rel'] == rel), None)
  return link['uri'] if link else None

def save_result(name, contents):
  with open('output/' + name + '.json', 'w') as outfile:
    json.dump(contents, outfile, indent=2)

MYJOHNDEERE_V3_JSON_HEADERS = { 
                                'Accept': 'application/vnd.deere.axiom.v3+json',
                                'Content-Type': 'application/vnd.deere.axiom.v3+json',
                                'Accept-UOM-System': 'ENGLISH'
                              }

#API_CATALOG_URI = 'https://sandboxapi.deere.com/platform/'
API_CATALOG_URI = 'https://partnerapi.deere.com/platform/'

def init_session():
  api_catalog_response = get(API_CATALOG_URI)
  organizations_link = find_link(api_catalog_response['links'], 'organizations')
  return organizations_link

def loop_tokens(func):
  tokens = get_tokens()
  for index, row in tokens.iterrows():
    print("Trying: " + row["username"])
    token_saver(json.loads(row["data"]))
    try:
      organizations_link = init_session()
      func(organizations_link, row["username"])
    except InvalidGrantError as error:
      print("Expired refresh token")

