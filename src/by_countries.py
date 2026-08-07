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


with open("templates/country.html", "r", encoding="utf-8") as f:
    country_template = f.read()

for code, notes in result.items():
    out = Path(f"pages/{code}")
    out.mkdir(exist_ok=True, parents=True)

    with open(f"{out}/index.html", "w", encoding="utf-8") as file:
        html = country_template.replace("<!-- Country code -->", code)
        s = ""
        for l in notes:
            closed = [f'<a {"class=commented " if n[1] == 1 else "class=stop_word " if n[1] == 2 else "class=commented stop_word " if n[1] == 3 else "" }href="https://openstreetmap.org/note/{n[0]}" target="_blank" rel="noopener noreferrer">{n[0]}</a>' for n in l["c"]]
            opened = [f'<a {"class=commented " if n[1] == 1 else "class=stop_word " if n[1] == 2 else "class=commented stop_word " if n[1] == 3 else "" }href="https://openstreetmap.org/note/{n[0]}" target="_blank" rel="noopener noreferrer">{n[0]}</a>' for n in l["o"]]
            s += f"<tr>\n  <td>{", ".join(closed)}</td>\n  <td>{", ".join(opened)}</td>\n</tr>\n"
        html = html.replace("<!-- Notes table -->", s)
        file.write(html)

out = Path(f"pages")
out.mkdir(exist_ok=True)

with open(f"{out}/index.html", "w", encoding="utf-8") as file:
    with open("templates/main.html", "r", encoding="utf-8") as f:
        main_template = f.read()
    countries = [f'<a href="./{code}">{code}</a>' for code, notes in result.items()]
    file.write(main_template.replace("<!-- Countries list -->", " ".join(countries)))
