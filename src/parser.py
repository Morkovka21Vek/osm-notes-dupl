import xml.etree.ElementTree as ET
import json
import struct

record = struct.Struct("<IiiBI") # if id or uid > 2^32-1 use Q

users = {}

with open("notes.bin", "wb") as out:
    for event, elem in ET.iterparse("planet-notes-latest.osn", events=("end",)):
        if elem.tag == "note":
            last_closer_uid = 0
            for comment in elem.findall("comment"):
                if comment.attrib.get("action") == "closed":
                    last_closer_uid = comment.attrib["uid"]
                    users[comment.attrib["uid"]] = comment.attrib["user"]

            out.write(record.pack(
                int(elem.attrib["id"]),
                int(round(float(elem.attrib["lat"]) * 10_000_000)),
                int(round(float(elem.attrib["lon"]) * 10_000_000)),
                int("closed_at" in elem.attrib),
                int(last_closer_uid)
            ))

            elem.clear()

with open("users.json", "w", encoding="utf-8") as file:
    json.dump(users, file, ensure_ascii=False, separators=(",", ":"))

