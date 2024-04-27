import pandas as pd
from request_utils import get, loop_tokens
from datetime import datetime

def get_planting(link, field_id):
  link = f"{link}?cropSeason=2024&fieldOperationType=SEEDING"
  field_operations_response = get(link)
  return field_operations_response

def process_fields(organizations_link, username):
  for index, row in fields[fields.user_name==username].iterrows():
    operations_link = f"{organizations_link}/{row['jd_org_id']}/fields/{row['jd_field_id']}/fieldOperations"
    planting_response = get_planting(operations_link, row['jd_field_id'])
    if planting_response['total'] > 0:
      operation = planting_response['values'][0]
      fields.at[index, 'planting_date'] = datetime.fromisoformat(operation['startDate']).strftime("%Y-%m-%d")
      fields.at[index, 'crop'] = operation['cropName']

def main():
  fields['planting_date'] = ''
  fields['crop'] = ''

  loop_tokens(process_fields)

  fields.to_csv("output/planting_date.csv", index=False)

fields = pd.read_csv("output/fields.csv")
if __name__ == "__main__":
  main()