from shapely.geometry import Point, shape
from shapely.strtree import STRtree

with open("osm-countries.geojson", "r", encoding="utf-8") as f:
    geojson = json.load(f)

polygons = []
countries = []

for feature in geojson["features"]:
    polygons.append(shape(feature["geometry"]))
    countries.append(feature["properties"]["tags"]["ISO3166-1"])
    #countries.append(feature["properties"]["tags"]["name"])

tree = STRtree(polygons)


def get_countries(lat, lon):
    point = Point(lon, lat)

    result = []
    for idx in tree.query(point):
        polygon = polygons[idx]
        if polygon.contains(point):
            result.append(countries[idx])

    if not result:
        return ["other"]
    return result
