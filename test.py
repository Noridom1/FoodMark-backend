from serpapi import GoogleSearch
import json
import requests

def get_directions(lat1, lon1, lat2, lon2):

    url = "http://router.project-osrm.org/route/v1/driving/{},{};{},{}?geometries=geojson".format(
    lon1, lat1, lon2, lat2
)
    response = requests.get(url).json()
    coords = response["routes"][0]["geometry"]["coordinates"]
    gps_points = [(lat, lng) for lng, lat in coords]
    return gps_points


# # Example usage:
# lat1, lon1 = 30.1934892, -97.6650096
# lat2, lon2 = 30.324629, -97.727882
# gps_points = get_directions(lat1,lon1,lat2,lon2)
# print(gps_points)
# geojson = {
#     "type": "FeatureCollection",
#     "features": [
#         {
#             "type": "Feature",
#             "geometry": {
#                 "type": "LineString",
#                 "coordinates": [[lon, lat] for lat, lon in gps_points]
#             },
#             "properties": {
#                 "name": "Driving Route"
#             }
#         }
#     ]
# }

# # Save to file
# with open("route.geojson", "w") as f:
#     json.dump(geojson, f, indent=2)

# print(json.dumps(geojson, indent=2))