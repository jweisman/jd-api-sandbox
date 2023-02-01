# My Version
""" def jd_to_geojson(multipolygon):
  geojson = {
    "type": "FeatureCollection",
    "features": [
      {
        "type": "Feature",
        "geometry": {
          "type": "MultiPolygon",
          "coordinates": []
        }
      }
    ]
  }
  for polygon in multipolygon:
    geojson["features"][0]["geometry"]["coordinates"].append(
      [jd_polygon_to_coordinate(polygon)])
  return geojson


def jd_polygon_to_coordinate(polygon):
  coordinates = []
  for point in polygon['rings'][0]['points']:
    coordinates.append([point["lon"], point["lat"]])
  return coordinates """

# From Taranis Web App JD Import (Avi)
def get_boundary(boundaries):
  active_boundary = None
  not_active_boundary = None
  for boundary in boundaries:
    polygons = []
    for multipolygon in boundary['multipolygons']:
      for ring in multipolygon['rings']:
        polygons.append(
          [[[pt['lon'], pt['lat']] for pt in ring['points']]]
        )
    converted_boundary = {
      'type': 'Feature',
      'area': boundary['area']['valueAsDouble'],
      'area_unit': boundary['area']['unit'],
      'geometry': {
          'type': 'MultiPolygon',
          'coordinates': polygons
      }
    }
    if boundary['active']:
      active_boundary = converted_boundary
    else:
      not_active_boundary = converted_boundary
  return active_boundary or not_active_boundary
