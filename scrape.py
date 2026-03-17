import requests
import json

urlW2 = "https://artist-lineup-cdn.tomorrowland.com/TL26BE-W1-9205196e-3eef-45c0-a82e-72aa1bb3cf8f.json"
urlW1 = "https://artist-lineup-cdn.tomorrowland.com/TL26BE-W2-9205196e-3eef-45c0-a82e-72aa1bb3cf8f.json"

resp = requests.get(urlW1)
resp.raise_for_status()

data = resp.json()

with open("lineupW1.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
print("Saved to lineupW1.json")

resp = requests.get(urlW2)
resp.raise_for_status()

data = resp.json()
with open("lineupW2.json", "w", encoding="utf-8") as f:
    json.dump(data, f, indent=2)
print("Saved to lineupW2.json")

