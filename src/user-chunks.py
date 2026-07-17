import json
import hashlib
from pathlib import Path

src = "users.json"
out = Path("users")
out.mkdir(exist_ok=True)

files = {}

with open(src, "r", encoding="utf-8") as f:
    data = json.load(f)

for uid, username in data.items():
    h = hashlib.md5(username.encode()).hexdigest()[:2]

    if h not in files:
        files[h] = open(out / f"{h}.json", "w", encoding="utf-8")
        files[h].write("{")
    else:
        files[h].write(",")

    files[h].write(
        #json.dumps({uid: username}, ensure_ascii=False)[1:-1]
        json.dumps({username: uid}, ensure_ascii=False)[1:-1]
    )

for f in files.values():
    f.write("}\n")
    f.close()
