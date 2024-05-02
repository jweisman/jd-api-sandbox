# John Deere API Sandbox

To set up the script:
1. Clone the repository
2. Install requirements: `pip install -r requirements.txt`
3. Add a `secret.py` file with the following fields:
```
CLIENT_ID = 'xxxx'
CLIENT_SECRET = 'xxxx'
DB_CONNECTION_STRING = 'postgresql://USER:PASSWORD@DB:PORT/mavrx'
```

## Scripts
The following scripts are available. Each script retrieves and loops over the available tokens.
* `get_field_operations`: Retrieves field operations such as seeding, tillage, and harvest
* `match_fields`: Retrieves field boundaries and matches fields based on overlapping area and exports to `output/fields.csv`
* `get_planting_date`: Retrieves planting dates for fields in the matched file and exports to `output/planting_date.csv`
* `get_organizations`: Retrieves all JD organizations the tokens provide access to and exports to `output/organizations.txt`

### Planting date process
The following process is used to retrieve planting dates:
1. Run `match_fields.py` to retrieve fields from JD and match to fields based on overlapping boundaries
2. Run `get_planting_date.py` to loop over fields and search for a planting operation