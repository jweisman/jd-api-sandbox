import pandas as pd
from request_utils import get, loop_tokens, find_link
from datetime import datetime

def get_planting(link, field_id):
  link = f"{link}?cropSeason={datetime.now().year}&fieldOperationType=SEEDING"
  field_operations_response = get(link)
  return field_operations_response

def process_fields(organizations_link, username):
  for index, row in fields[fields.user_name==username].iterrows():
    operations_link = f"{organizations_link}/{row['jd_org_id']}/fields/{row['jd_field_id']}/fieldOperations"
    planting_response = get_planting(operations_link, row['jd_field_id'])
    total_planting = planting_response['total']
    if total_planting > 0:
      operation = planting_response['values'][total_planting-1]
      fields.at[index, 'planting_date'] = datetime.fromisoformat(operation['startDate']).strftime("%Y-%m-%d")
      fields.at[index, 'crop'] = operation['cropName']

      measurements_link = find_link(operation['links'], 'seedingRateTarget')
      measurement_response = get(measurements_link)
      if measurement_response:
        fields.at[index, 'target_pop'] = measurement_response['averageMaterial']['value']
        fields.at[index, 'target_acres'] = measurement_response['area']['value']

def main():
  fields['planting_date'] = ''
  fields['crop'] = ''
  fields['target_pop'] = ''
  fields['target_acres'] = ''

  loop_tokens(process_fields)

  fields.to_csv("output/planting_date.csv", index=False)

fields = pd.read_csv("output/fields.csv")
if __name__ == "__main__":
  main()