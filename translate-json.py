import json

with open("./source-json/lineupW1.json", "r") as f:
    data = json.load(f)

artists_out = []

for perf in data.get("performances", []):
    for artist in perf.get("artists", []):
        artists_out.append({
            "name": artist.get("name"),
            "spotify": artist.get("spotify")  # will be None if missing
        })

with open("./processed-json/w1-artists.json", "w") as f:
    json.dump(artists_out, f, indent=2)
