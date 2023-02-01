from secret import CLIENT_ID, CLIENT_SECRET
from auth import WELL_KNOWN_TOKEN_URL, get_token, token_saver
from requests_oauthlib import OAuth2Session
from tabulate import tabulate
from utils import get_boundary
from datetime import datetime
import json

def get(protected_url):
  token = get_token()
  print('Getting ' + protected_url)
  client = OAuth2Session(CLIENT_ID, token=token, auto_refresh_url=WELL_KNOWN_TOKEN_URL,
    auto_refresh_kwargs={'client_id': CLIENT_ID, 'client_secret': CLIENT_SECRET}, token_updater=token_saver)
  response = client.get(protected_url, headers=MYJOHNDEERE_V3_JSON_HEADERS)
  return response.json() if response.status_code == 200 else response

def find_link(iterable, rel):
  link = next((link for link in iterable if link['rel'] == rel), None)
  return link['uri'] if link else None

def save_result(name, contents):
  with open('output/' + name + '.json', 'w') as outfile:
    json.dump(contents, outfile, indent=2)

MYJOHNDEERE_V3_JSON_HEADERS = { 'Accept': 'application/vnd.deere.axiom.v3+json',
                                'Content-Type': 'application/vnd.deere.axiom.v3+json'}

API_CATALOG_URI = 'https://sandboxapi.deere.com/platform/'
#API_CATALOG_URI = 'https://partnerapi.deere.com/platform/'

OPERATION_TYPES = ['seeding', 'tillage', 'harvest']

field_events = []

def process_organizations(link):
  organizations_response = get(link)
  #save_result('organizations', organizations_response)
  for organization in organizations_response['values']:
    print('Processing organization: ' + organization['name'])
    fields_link = find_link(organization['links'], 'fields')
    if fields_link: process_fields(fields_link)
  
  next_link = find_link(organization['links'], 'nextPage')
  if next_link: process_organizations(next_link)

def process_fields(link):
  # Get fields
  fields_response = get(link)

  # Loop through fields
  for field in fields_response['values']:
    print('Field: ' + field['name'])
    boundaries_response = get(find_link(field['links'], 'simplifiedBoundaries'))
    if boundaries_response['total'] >= 1:
      #geojson = jd_to_geojson(boundaries_response['values'][0]['multipolygons'])
      geojson = get_boundary(boundaries_response['values'])
      save_result(f"fields/{field['id']}-boundaries", geojson)
      operations_link = find_link(field['links'], 'fieldOperation')
      if operations_link: process_operations(operations_link, field['id'])

  next_link = find_link(fields_response['links'], 'nextPage')
  if next_link: process_fields(next_link)

def process_operations(link, field_id):
  # Get Field Operations
  field_operations_response = get(link)
  # Get operations
  for operation in filter(lambda op: op['fieldOperationType'] in OPERATION_TYPES, field_operations_response['values']):
    match operation['fieldOperationType']:
      case 'seeding':
        field_events.append({ 'field': field_id, 'date': datetime.fromisoformat(operation['startDate']).strftime("%d-%b-%Y"), 'event_type': 'PLANTING', 'event_detail': operation['cropName']})
      case 'harvest':
        field_events.append({ 'field': field_id, 'date': datetime.fromisoformat(operation['startDate']).strftime("%d-%b-%Y"), 'event_type': 'HARVEST', 'event_detail': ''})
      case 'tillage':
        tillage_link = find_link(operation['links'], 'tillageSpeedResult')
        tillage_response = get(tillage_link)
        field_events.append({ 'field': field_id, 'date': datetime.fromisoformat(operation['startDate']).strftime("%d-%b-%Y"), 'event_type': 'TILLAGE', 'event_detail': str(tillage_response['averageSpeed']['value'])})

  next_link = find_link(field_operations_response['links'], 'nextPage')
  if next_link: process_operations(next_link, field_id)

# Get API Catalog
api_catalog_response = get(API_CATALOG_URI)
organizations_link = find_link(api_catalog_response['links'], 'organizations')
process_organizations(organizations_link)
with open('output/results.txt', 'w') as f:
  print(tabulate(field_events, headers="keys"), file=f)