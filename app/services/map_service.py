import requests
import json
from typing import List
from pydantic import BaseModel

class DestinationNode(BaseModel):
    lat: float
    lng: float



def get_directions(points: List[tuple[float, float]]):
    if len(points) < 2:
        raise ValueError("At least two points (start and end) are required")

    coords_str = ";".join([f"{lon},{lat}" for lat, lon in points])
    url = f"http://router.project-osrm.org/route/v1/driving/{coords_str}?geometries=geojson"
    response = requests.get(url).json()

    coords = response["routes"][0]["geometry"]["coordinates"]
    gps_points = [(lat, lon) for lon, lat in coords]
    return gps_points



# # ✅ Example usage with 3 or 4 waypoints
# points = [
#     (30.1934892, -97.6650096),   # Start
#     (30.2500000, -97.7000000),   # Stop 1
#     (30.2800000, -97.7100000),   # Stop 2 (optional)
#     (30.324629, -97.727882)      # Destination
# ]

# gps_points = get_directions(points)

# print("Number of GPS points:", len(gps_points))

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
