import struct
from collections import defaultdict
import json

record = struct.Struct("<IiiBI")

notes = {}

with open("notes.bin", "rb") as f:
    while True:
        data = f.read(record.size)
        if not data:
            break

        note_id, lat, lon, closed, uid = record.unpack(data)

        key = (lat, lon)

        notes.setdefault(key, []).append({
            "id": note_id,
            "closed": bool(closed),
            "uid": uid,
        })

result = defaultdict(list)

for (lat, lon), location_notes in notes.items():
    users = set(
        n["uid"] for n in location_notes if n["closed"]
    )

    for uid in users:

        if uid == 0:
            continue

        opened_notes = []
        closed_notes = []

        for note in location_notes:
            if note["closed"] and note["uid"] == uid:
                closed_notes.append(note["id"])
            elif not note["closed"]:
                opened_notes.append(note["id"])

        if closed_notes:
            result[uid].append({
                "o": opened_notes,
                "c": closed_notes,
            })

with open("by_users.json", "w", encoding="utf-8") as file:
    json.dump(result, file, ensure_ascii=False, separators=(",", ":"))
