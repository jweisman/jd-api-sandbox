import pandas as pd
from request_utils import get, find_link, save_result, loop_tokens
from tabulate import tabulate
from utils import get_boundary
from datetime import datetime

OPERATIONS = {
  'seeding': {
    'event_type': lambda o: 'COVER' if datetime.fromisoformat(o['startDate']).month > 7 else 'PLANTING',
    'event_detail': lambda o: o['cropName']
  },
  'tillage': {
    'event_type': lambda o: 'TILLAGE',
    'event_detail': lambda o: get_tillage_speed(o)
  },
  'harvest': {
    'event_type': lambda o: 'HARVEST',
    'event_detail': lambda o: ''
  }
}

def get_tillage_speed(o):
  tillage_link = find_link(o['links'], 'tillageSpeedResult')
  if tillage_link:
    tillage_response = get(tillage_link) 
    return 'CONVENTIONAL' if tillage_response['averageSpeed']['value'] < 7 else 'REDUCED' 
  else: return 'UNKNOWN'
  
def process_organizations(link, user_name):
  organizations_response = get(link)
  for organization in organizations_response['values']:
    print(f"Processing organization: ${organization['name']}")
    fields_link = find_link(organization['links'], 'fields')
    process_fields(fields_link, organization['name']) if fields_link else print(f"Skipping organization ${organization['name']}")
  
  next_link = find_link(organizations_response['links'], 'nextPage')
  if next_link: process_organizations(next_link)

def process_fields(link, org_name):
  # Get fields
  fields_response = get(link)

  # Loop through fields
  for field in fields_response['values']:
    print('Field: ' + field['name'])
    boundaries_response = get(find_link(field['links'], 'simplifiedBoundaries'))
    if boundaries_response['total'] >= 1:
      geojson = get_boundary(boundaries_response['values'])
      save_result(f"fields/{field['id']}-boundaries", geojson)
      operations_link = find_link(field['links'], 'fieldOperation')
      if operations_link: process_operations(operations_link, field['id'], field['name'], org_name)

  next_link = find_link(fields_response['links'], 'nextPage')
  if next_link: process_fields(next_link, org_name)

def process_operations(link, field_id, field_name, org_name):
  # Get Field Operations
  field_operations_response = get(link)
  # Get operations
  for operation in filter(lambda op: op['fieldOperationType'] in OPERATIONS.keys(), field_operations_response['values']):
    operation_def = OPERATIONS[operation['fieldOperationType']]
    field_events.append({ 
      'field_id': field_id,
      'field_name': field_name,
      'org_name': org_name,
      'date': datetime.fromisoformat(operation['startDate']).strftime("%d-%b-%Y"),
      'event_type': operation_def['event_type'](operation),
      'event_detail': operation_def['event_detail'](operation)
    })
  next_link = find_link(field_operations_response['links'], 'nextPage')
  if next_link: process_operations(next_link, field_id, field_name, org_name)

def main():
  loop_tokens(process_organizations)
  with open('output/results.txt', 'w') as f:
    print(tabulate(field_events, headers="keys"), file=f)

field_events = []

if __name__ == "__main__":
  main()