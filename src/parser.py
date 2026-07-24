import xml.etree.ElementTree as ET
import struct

record = struct.Struct("<IiiBI") # if id or uid > 2^32-1 use Q

with open("notes.bin", "wb") as out:
    for event, elem in ET.iterparse("planet-notes-latest.osn", events=("end",)):
        if elem.tag == "note":
            last_closer_uid = 0
            for comment in elem.findall("comment"):
                if comment.attrib.get("action") == "closed":
                    last_closer_uid = comment.attrib["uid"]

            out.write(record.pack(
                int(elem.attrib["id"]),
                #int(round(float(elem.attrib["lat"]) * 10_000_000)),
                #int(round(float(elem.attrib["lon"]) * 10_000_000)),
                int(float(elem.attrib["lat"]) * 10_000_000),
                int(float(elem.attrib["lon"]) * 10_000_000),
                int("closed_at" in elem.attrib),
                int(last_closer_uid)
            ))

            elem.clear()

