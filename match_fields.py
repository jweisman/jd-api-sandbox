from db import find_field_by_intersect
import pandas as pd
from request_utils import get, find_link, save_result, loop_tokens
from utils import get_boundary

fields = []

def find_taranis_field(boundaries):
    df = find_field_by_intersect(boundaries)
    return df[df.percent_of_intersection>79].sort_values('percent_of_intersection', ascending=False)

def process_fields(link, org_id, org_name, user_name):
  # Get fields
  fields_response = get(link)
  # Loop through fields
  for field in fields_response['values']:
    boundaries = field.get('boundaries')
    if boundaries and len(boundaries) > 0:
      geojson = get_boundary(boundaries)
      taranis_field = find_taranis_field(geojson)
      if len(taranis_field) > 0:
        taranis_field = taranis_field.iloc[0]
        fields.append({ 
          'jd_field_id': field['id'],
          'jd_field_name': field['name'],
          'jd_org_id': org_id,
          'jd_org_name': org_name,
          'taranis_field_id': taranis_field['id'],
          'taranis_field_name': taranis_field['field_name'],
          'taranis_client_name': taranis_field['client_name'],
          'taranis_org_name': taranis_field['organization_name'],
          'percent': taranis_field['percent_of_intersection'],
          'current_plan': taranis_field['current_plan'],
          'user_name': user_name
        })    

  next_link = find_link(fields_response['links'], 'nextPage')
  if next_link: process_fields(next_link, org_id, org_name, user_name)

def process_organizations(link, user_name):
  organizations_response = get(link)
  for organization in organizations_response['values']:
    print(f"Processing organization: ${organization['name']}")
    fields_link = find_link(organization['links'], 'fields')
    if fields_link:
      process_fields(f"{fields_link}?embed=simplifiedBoundaries&itemLimit=25", organization['id'], organization['name'], user_name) 
    else: print(f"Skipping organization ${organization['name']}")
  
  next_link = find_link(organizations_response['links'], 'nextPage')
  if next_link: process_organizations(next_link, user_name)

def main():
  loop_tokens(process_organizations)

  df = pd.DataFrame(fields) 
  df.to_csv("output/fields.csv", index=False)

if __name__ == "__main__":
  main()