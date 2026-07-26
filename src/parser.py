import xml.etree.ElementTree as ET
import struct
import wordlist

record = struct.Struct("<IiiBBIB") # if id or uid > 2^32-1 use Q

with open("notes.bin", "wb") as out:
    for event, elem in ET.iterparse("planet-notes-latest.osn", events=("end",)):
        if elem.tag == "note":
            last_closer_uid = 0
            commented = False
            stop_word = False

            for comment in elem.findall("comment"):
                if comment.attrib.get("action") == "closed":
                    last_closer_uid = comment.attrib["uid"]
                elif comment.attrib.get("action") == "commented" and comment.attrib.get("uid"):
                    commented = True
                elif comment.attrib.get("action") == "opened":
                    continue

                text = (comment.text or "").lower()
                if any(word in text for word in wordlist.DUPLICATE_STOP_WORDS):
                    stop_word = True

            out.write(record.pack(
                int(elem.attrib["id"]),
                int(float(elem.attrib["lat"]) * 10_000_000),
                int(float(elem.attrib["lon"]) * 10_000_000),
                commented,
                int("closed_at" in elem.attrib),
                int(last_closer_uid),
                stop_word
            ))

            elem.clear()

