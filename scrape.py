import requests
import json

sourceJsonFolder = "source-json/"

urlStages = "https://artist-lineup-cdn.tomorrowland.com/stages-TL26BE-9205196e-3eef-45c0-a82e-72aa1bb3cf8f.json"
urlW2 = "https://artist-lineup-cdn.tomorrowland.com/TL26BE-W2-9205196e-3eef-45c0-a82e-72aa1bb3cf8f.json"
urlW1 = "https://artist-lineup-cdn.tomorrowland.com/TL26BE-W1-9205196e-3eef-45c0-a82e-72aa1bb3cf8f.json"

resp = requests.get(urlStages)
resp.raise_for_status()

data = resp.json()

with open(sourceJsonFolder + "stages.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
print("Saved stages")

resp = requests.get(urlW1)
resp.raise_for_status()

data = resp.json()

with open(sourceJsonFolder + "lineupW1.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
print("Saved lineupW1")

resp = requests.get(urlW2)
resp.raise_for_status()

data = resp.json()
with open(sourceJsonFolder + "lineupW2.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
print("Saved lineupW2")

