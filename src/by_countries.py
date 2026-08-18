import json
import csv
from collections import defaultdict
from shapely.geometry import Point, shape
from shapely.strtree import STRtree
from pathlib import Path
import html

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

result_closed = defaultdict(list)

with open("dupl_closed_notes.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        lat = float(row["lat"]) / 10_000_000
        lon = float(row["lon"]) / 10_000_000

        notes = {"o": [], "c": [], "time": 0}

        for item in row["open_notes"].split(";"):
            notes["o"].append(tuple(map(int, item.split(":"))))

        for item in row["closed_notes"].split(";"):
            notes["c"].append(tuple(map(int, item.split(":"))))

        notes["time"] = int(row["time"])

        for c in get_countries(lat, lon):
            result_closed[c].append(notes)


with open("src/templates/country_closed.html", "r", encoding="utf-8") as f:
    country_template = f.read()

for code, notes in result_closed.items():
    notes.sort(key=lambda x: x["time"], reverse=True)

    out = Path(f"pages/closed/{code}")
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


result_opened = defaultdict(list)

with open("dupl_opened_notes.csv", "r", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)

    for row in reader:
        lat = float(row["lat"]) / 10_000_000
        lon = float(row["lon"]) / 10_000_000

        notes = {"o": [], "time": 0}

        for item in row["open_notes"].split(";"):
            notes["o"].append(tuple(map(int, item.split(":"))))

        notes["time"] = int(row["time"])

        for c in get_countries(lat, lon):
            result_opened[c].append(notes)


with open("src/templates/country_opened.html", "r", encoding="utf-8") as f:
    country_template = f.read()

for code, notes in result_opened.items():
    notes.sort(key=lambda x: x["time"], reverse=True)

    out = Path(f"pages/opened/{code}")
    out.mkdir(exist_ok=True, parents=True)

    with open(f"{out}/index.html", "w", encoding="utf-8") as file:
        html = country_template.replace("<!-- Country code -->", code)
        s = ""
        for l in notes:
            opened = [f'  <li><a {"class=commented " if n[1] == 1 else "class=stop_word " if n[1] == 2 else "class=commented stop_word " if n[1] == 3 else "" }href="https://openstreetmap.org/note/{n[0]}" target="_blank" rel="noopener noreferrer">{n[0]}</a></li>\n' for n in l["o"]]
            s += ", ".join(closed)
        html = html.replace("<!-- Notes list -->", s)
        file.write(html)


out = Path(f"pages")
out.mkdir(exist_ok=True)

with open(f"{out}/index.html", "w", encoding="utf-8") as file:
    with open("src/templates/main.html", "r", encoding="utf-8") as f:
        main_template = f.read()

    countries = [f'<a href="./closed/{code}/">{code}</a>' for code, notes in result_closed.items()]
    s = main_template.replace("<!-- Countries closed list -->", " ".join(countries))

    countries = [f'<a href="./opened/{code}/">{code}</a>' for code, notes in result_opened.items()]
    s = s.replace("<!-- Countries opened list -->", " ".join(countries))
    file.write(s)
