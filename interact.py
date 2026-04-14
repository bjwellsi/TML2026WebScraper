import json
import os

FILE_PATH = "./processed-json/w1-artists.json"


def load_data():
    with open(FILE_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def save_data(data):
    # write to temp file first for safety
    tmp_path = FILE_PATH + ".tmp"
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    os.replace(tmp_path, FILE_PATH)


def main():
    data = load_data()

    total = len(data)
    updated = 0

    for i, artist in enumerate(data):
        if artist.get("spotify"):
            continue

        name = artist.get("name", "UNKNOWN")

        print(f"\n[{i+1}/{total}] {name}")
        print("Enter Spotify URL (or 's' to skip, 'q' to quit):")

        user_input = input("> ").strip()

        if user_input.lower() == "q":
            print("Quitting early...")
            break

        if user_input.lower() == "s" or user_input == "":
            continue

        # basic validation
        if "spotify.com" not in user_input:
            print("⚠️  That doesn't look like a Spotify URL. Skipping.")
            continue

        artist["spotify"] = user_input
        updated += 1

        save_data(data)  # save after every update

    print(f"\nDone. Updated {updated} artists.")


if __name__ == "__main__":
    main()
