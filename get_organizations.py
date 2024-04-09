from request_utils import find_link, get, loop_tokens
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError
import json

def process_organizations(link, user_name):
  organizations_response = get(link)
  for organization in organizations_response['values']:
    print(f'{user_name},{organization["name"]}')
  
  next_link = find_link(organizations_response['links'], 'nextPage')
  if next_link: process_organizations(next_link, user_name)

def main():
  loop_tokens(process_organizations)

if __name__ == "__main__":
  main()