import json

files = ["admin.json", "auth.json", "chess_python.json", "contenttypes.json", "sessions.json"]

all_data = []

for filename in files:
    with open(filename, "r", encoding="utf-8") as f:
        data = json.load(f)
        all_data.extend(data)

with open("data.json", "w", encoding="utf-8") as f:
    json.dump(all_data, f, ensure_ascii=False, indent=2)

print("data.json created successfully without BOM!")
