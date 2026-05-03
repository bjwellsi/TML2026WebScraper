import os
import requests
import json
import webbrowser
import base64
import secrets
import socket
from urllib.parse import urlparse, parse_qs, urlencode
from dotenv import load_dotenv

load_dotenv()

spotify_base_url = "https://api.spotify.com/v1"
client_id = os.environ['SPOTIFY_CLIENT_ID']
client_secret = os.environ['SPOTIFY_CLIENT_SECRET']
redirect_uri = "http://127.0.0.1:3000/callback"
spotify_playlist_id = os.environ['SPOTIFY_PLAYLIST_ID']

def get_generic_access_token():

    auth_url = 'https://accounts.spotify.com/api/token'
    auth_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    auth_body = 'grant_type=client_credentials&client_id=' + client_id + '&client_secret=' + client_secret

    auth_resp = requests.post(auth_url, data = auth_body, headers = auth_headers)

    if auth_resp.status_code == 200:
        return auth_resp.json()["access_token"]

    else:
        raise Exception("No access token returned - " + json.dumps(auth_resp.json()))

def get_user_access_token():
    #for now this script is purely a single run kind of deal
    #Meaning this code is going to be generated fresh on every run 
    state = secrets.token_urlsafe(32)
    scopes = "playlist-modify-private playlist-modify-public"

    params = {
        "response_type": "code",
        "client_id": client_id,
        "scope": scopes,
        "redirect_uri": redirect_uri,
        "state": state
    }

    code_url = "https://accounts.spotify.com/authorize?" + urlencode(params)

    print("Opening spotify to request permissions")
    webbrowser.open(code_url)
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind(('127.0.0.1', 3000))

    s.listen(5)
    print("Waiting for callback response")

    conn, addr = s.accept()
    print("Received callback response")

    data = conn.recv(4096)
    callback_response = data.decode()
    parsed_url = callback_response.split("\r\n")[0].split(" ")[1]
    params = parse_qs(urlparse(parsed_url).query)
    response_state = params.get("state", [None])[0]
    conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nLogin complete. You can close this tab.")
    conn.close()

    #once you get a response
    if response_state != state:
        #state changed, no good
        return

    code = params.get("code", [None])[0]

    token_url = "https://accounts.spotify.com/api/token"
    token_body = {"grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri}
    client_creds = client_id + ":" + client_secret
    creds_bytes = client_creds.encode("utf-8")
    creds_base64 = base64.b64encode(creds_bytes)
    token_headers = {"Authorization": "Basic " + creds_base64.decode("utf-8"), "Content-Type": "application/x-www-form-urlencoded"}
    auth_resp = requests.post(token_url, data = token_body, headers = token_headers)

    if auth_resp.status_code == 200:
        #not storing anything other than access token rn (eg refresh token)
        # bc again, this is a stateless script
        access_token = auth_resp.json()["access_token"] 
        return access_token
    else:
        raise Exception("No access token returned - " + json.dumps(auth_resp.json()))
    return

    
def get_artist_top_song_ids(artist_id):
    access_token = get_generic_access_token()

    url = spotify_base_url + "/artists/" + artist_id + "/top-tracks"
    resp = requests.get(url, headers = {"Authorization": "Bearer  " + access_token})
    if resp.status_code == 200:
        songs = resp.json()
        song_ids = []

        for song in songs["tracks"]:
            song_ids.append(song["id"])

        return song_ids
    else:
        raise Exception("No songs returned - " + json.dumps(resp.json()))
    return
     
def retrieve_artist_id_list():
    file_location = './processed-json/w1-artists.json'
    with open(file_location, 'r', encoding='utf-8') as arts:
        artist_ids = []

        artists = json.load(arts)
        for artist in artists:
            if artist.get("spotify") is None:
                continue

            url = artist["spotify"]
            id_ind = url.index("artist/") + 7
            artist_id = url[id_ind:]
            
            #don't want dupes
            if artist_id in artist_ids:
                continue

            artist_ids.append(artist_id)
            
        return artist_ids
    return

def generate_song_list(limit = None):
    artists = retrieve_artist_id_list() 
    songs = []
    for artist_id in artists:
        artist_songs = get_artist_top_song_ids(artist_id)
        if limit is not None:
            if limit <= 0:
                break

            overflow = (len(artist_songs) - limit)
            if overflow >= 0:
                artist_songs = artist_songs[0:limit]
                limit = 0
            else:
                limit -= len(artist_songs)

        songs.extend(artist_songs)
    return songs

def print_songs_to_file(songs):

    with open("./processed-json/top-songs.json", "w") as f:
        json.dump(songs, f, indent=2)

def read_songs_from_file():
    with open("./processed-json/top-songs.json", "r") as f:
        return json.load(f)


def create_or_update_playlist(songs, playlist_id, playlist_name, playlist_desc):
    if playlist_id is None and playlist_name is None:
        return

    #get access token
    access_token = get_user_access_token()

    if playlist_id is None:
        #make a new playlist
        req_url = spotify_base_url + "/me/playlists"
        req_body = data = {"name": playlist_name, "description": playlist_desc}
        req_headers = {"Authorization": "Bearer " + access_token}
        resp = requests.post(req_url, json = req_body, headers = req_headers) 
        print(req_body)
        if resp.status_code == 200:
            playlist_id = resp.json()["id"]
            print("Playlist created. ID: " + playlist_id)
        else:
            raise Exception("Failed to create playlist - " + json.dumps(resp.json()))

    song_url = spotify_base_url + "/me/playlists/" + playlist_id + "/items"
    print(song_url)
    for song in songs:
        song_body = {"uris": ["spotify:track:" + song]}
        print(song_body)
        resp = requests.post(song_url, json = song_body, headers = {"Authorization": "Bearer " + access_token, "Content-Type": "application/json"})
        if resp.status_code != 200:
            raise Exception("Failed to insert song into playlist - " + json.dumps(resp.json()))

    return playlist_id
    

def main():
    #print_songs_to_file(generate_song_list())

    songs = read_songs_from_file()
    #create_or_update_playlist(songs, None, "Tomorrowland 2026 Artists Weekend 1", "Top songs from all the artists I could find on spotify")
    create_or_update_playlist(songs, spotify_playlist_id, None, None)

if __name__ == "__main__":
    main()
