import struct
from collections import defaultdict
import csv

record = struct.Struct("<IiiBIBQ")

notes = defaultdict(lambda: {"o": [], "c": [], "time": 0})

with open("notes.bin", "rb") as f:
    while True:
        data = f.read(record.size)
        if not data:
            break

        note_id, lat, lon, commented, uid, stop_word, time = record.unpack(data)
        if uid in [3199858, 5060057]: # bot accounts
            continue

        notes[(lat, lon)]["c" if uid != 0 else "o"].append((note_id, commented+stop_word*2))
        notes[(lat, lon)]["time"] = max(time, notes[(lat, lon)]["time"])

with open("dupl_closed_notes.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["lat", "lon", "time", "open_notes", "closed_notes"])

    for (lat, lon), group in notes.items():
        if group["o"] and group["c"]:
            writer.writerow([
                lat,
                lon,
                group["time"],
                ";".join(f"{note_id}:{score}" for note_id, score in group["o"]),
                ";".join(f"{note_id}:{score}" for note_id, score in group["c"]),
            ])

with open("dupl_opened_notes.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["lat", "lon", "time", "open_notes"])

    for (lat, lon), group in notes.items():
        if len(group["o"]) > 1:
            writer.writerow([
                lat,
                lon,
                group["time"],
                ";".join(f"{note_id}:{score}" for note_id, score in group["o"]),
            ])

