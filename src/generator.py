import struct
from collections import defaultdict
import json

record = struct.Struct("<IiiBI")

notes = defaultdict(lambda: {"o": [], "c": []})

with open("notes.bin", "rb") as f:
    while True:
        data = f.read(record.size)
        if not data:
            break

        note_id, lat, lon, closed, _ = record.unpack(data)
        notes[(lat, lon)]["c" if closed else "o"].append(note_id)

#result = {f"{lat*0.0000001};{lon*0.0000001}": group for (lat, lon), group in notes.items() if group["o"] and group["c"]}
result = {f"{lat};{lon}": group for (lat, lon), group in notes.items() if group["o"] and group["c"]}

with open("dupl_notes.json", "w", encoding="utf-8") as file:
    json.dump(result, file, ensure_ascii=False, separators=(",", ":"))
    #json.dump(result, file, ensure_ascii=False, indent=4)
