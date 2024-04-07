from sqlalchemy import create_engine, text
from secret import DB_CONNECTION_STRING
import pandas as pd
import geojson
from shapely.geometry import shape
import json

def get_engine():
  return create_engine(DB_CONNECTION_STRING) 

INTERNAL_ORG_IDS = [2975,2976,4308,4336,4518,4519,4520,4521,4522,4523,4524,4525,4637,4652,4660,5101,5127,5139,5140,5141,5142,5143,5162,5179,5711,5712,5721,5751,5763,5768,5769,5806,5819,5832,5841,5873,5896,5903,5904,5906,5910,5925,5952,5995,6005,6009,6010,6011,6024,6046,6047,6056,6066,6083,6106,6107,6108,6115,6129,6130,6160,6192,6224,6225,6243,6254,6255,6272,6273,6274,6287,6294,6298,6322,6333,6337,6338,6348,6353,6369,6371,6374,6438,6499,6502,6505,6531,6541,6550,6558,6581,6582,6587,6599,6604,6625,6628,6629,6638,6644,6650,6703,6729,6730,6737,6746,6771,6793,6795,6833,6894,6911,6927,6928,6929,6939,6945,6950,6964,6965,6967,6970,6977,7000,7003,7027,7028,7029,7041,7042,7043,7047,7048,7059,7060,7061,7081,7089,7091,7094,7099,7100,7101,7102]

ENGINE = get_engine()

def get_tokens():
  query = text ("""select username, data, user_id  
              from partner_partnerusercredentials pp
              where pp.modified > '2023-01-01' 
              and partner = 'john deere'
              and username not in ('X050896', 'naama.zarfati@taranis.ag', 'IdoHlevy','aviklaiman', 'josh.weisman@taranis.com')
              """)

  with ENGINE.connect() as conn:
    df = pd.read_sql_query(
      sql = query,
      con = conn
    )
    return df
  
def find_field_by_intersect(boundaries):
  # Query the database to check if the geometry intersects with any field
  org_ids =  ",".join(str(x) for x in INTERNAL_ORG_IDS)

  query = text(f"""WITH geom_json AS 
               (SELECT ST_SetSRID(ST_MakeValid(ST_GeomFromText(:wkt)), 4326) as geojson_boundary) 
                select f.id, f.name as field_name, c.name as client_name, ol.name as organization_name,
                CASE
                WHEN ST_Area(the_geom) = 0 THEN null
                ELSE ST_Area(ST_Intersection(the_geom, geojson_boundary)) / ST_Area(the_geom) * 100
                END AS percent_of_intersection 
                FROM fields f, geom_json, farm fm, client c, organization_level ol 
                WHERE ST_Intersects(the_geom, geojson_boundary)=true and f.is_deleted =false
                and f.farm_id = fm.id
                and f.is_deleted = false
                and fm.client_id = c.id
                and c.organization_level_id = ol.id
              and c.organization_level_id not in ({org_ids})""")
  with ENGINE.connect() as conn:
    df = pd.read_sql_query(
      sql = query,
      params={"wkt": shape(geojson.loads(json.dumps(boundaries["geometry"]))).wkt},
      con = conn
    )
    return df