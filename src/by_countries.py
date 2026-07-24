import json
from collections import defaultdict
from shapely.geometry import Point, shape
from shapely.strtree import STRtree
from pathlib import Path
import html

with open("dupl_notes.json", "r", encoding="utf-8") as f:
    data = json.load(f)

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

result = defaultdict(list)

for pos, notes in data.items():
    lat, lon = map(float, pos.split(';'))

    lat = lat / 10_000_000
    lon = lon / 10_000_000

    for c in get_countries(lat, lon):
        result[c].append(notes)


for code, notes in result.items():
    out = Path(f"countries/{code}")
    out.mkdir(parents=True, exist_ok=True)

    with open(f"{out}/index.md", "w", encoding="utf-8") as file:
        s = f"""
# {code}
[home](../)

| Closed | Opened |
| --- | --- |
"""
        for l in notes:
            closed = [f"[{n}](https://openstreetmap.org/note/{n})" for n in l["c"]]
            opened = [f"[{n}](https://openstreetmap.org/note/{n})" for n in l["o"]]
            s += f"| {", ".join(closed)} | {", ".join(opened)} |\n"
        file.write(s)

with open(f"index.md", "w", encoding="utf-8") as file:
    countries = [f"[{code}](./{code})" for code, notes in result.items()]
    s = f"""
# OSM Notes Duplicates

> A list of potential duplicate OpenStreetMap notes. Each entry contains both open and closed notes created at the same coordinates.

{" ".join(countries)}


> Countries boundaries from [osm-countries-geojson](https://osm-countries-geojson.monicz.dev). Data [©OpenStreetMap](https://www.openstreetmap.org) contributors.
"""
    file.write(s)
