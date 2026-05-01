import os
import requests
import json
import webbrowser
import base64
import secrets
import socket
from urllib.parse import urlparse, parse_qs
from dotenv import load_dotenv

load_dotenv()

spotify_base_url = "https://api.spotify.com/v1"
client_id = os.environ['SPOTIFY_CLIENT_ID']
client_secret = os.environ['SPOTIFY_CLIENT_SECRET']
redirect_uri = "http://localhost:3000/callback"

def get_generic_access_token():

    auth_url = 'https://accounts.spotify.com/api/token'
    auth_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    auth_body = 'grant_type=client_credentials&client_id=' + client_id + 'client_secret=' + client_secret

    auth_resp = requests.post(auth_url, data = auth_body, headers = auth_headers)
    
    if auth_resp.status_code == 200:
        return auth_resp.text.access_token

    else:
        raise Exception("No access token returned - " + auth_resp)

def get_user_access_token():
    #for now this script is purely a single run kind of deal
    #Meaning this code is going to be generated fresh on every run 
    code_url = spotify_base_url + "/authorize?"
    state = secrets.token_urlsafe(32)
    scopes = "playlist-modify-private playlist-modify-public"
    code_url += "client_id=" + client_id + "&response_type=code&redirect_uri=" + redirect_uri + "&state=" + state + "&scope=" + scopes 

    print("Opening spotify to request permissions")
    webbrowser.open(code_url)
    
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.bind(('localhost', 3000))

    s.listen(5)
    print("Waiting for callback response")

    conn, addr = s.accept()
    print("Received callback response")

    data = conn.recv(4096)
    callback_response = data.decode()
    parsed_url = callback_response.split("\r\n")[0].split(" ")[1]
    params = parse_qs(parsed_url.query)
    response_state = params.get("state", [None])[0]
    conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: text/html\r\n\r\nLogin complete. You can close this tab.")
    onn.close()

    #once you get a response
    if response_state != state:
        #state changed, no good
        return

    code = params.get("code", [None])[0]

    token_url = spotify_base_url + "/api/token"
    token_body = {"grant_type": "authorization_code", "code": code, "redirect_uri": redirect_uri}
    client_creds = client_id + ":" + client_secret
    creds_bytes = client_creds.encode("utf-8")
    creds_base64 = base64.b64encode(creds_bytes)
    token_headers = {"authorization": "Basic " + creds_base64, "Content-Type": "application/x-www-form-urlencoded"}
    auth_resp = requests.post(token_url, data = token_body, headers = token_headers)

    if auth_resp.status_code == 200:
        #not storing anything other than access token rn (eg refresh token)
        # bc again, this is a stateless script
        access_token = auth_resp.data["access_token"] 
        return access_token
    else:
        raise Exception("No access token returned -" + auth_resp)
    return

    
def get_artist_top_song_ids(artist_id):
    access_token = get_generic_access_token()

    url = spotify_base_url + "/artists?"
    resp = requests.get(url, headers = {"Authorization": "Bearer  " + access_token})
    if resp.status_code == 200:
        songs = resp.text
        song_ids = []

        for song in songs:
            song_ids.append(song["id"])

        return song_ids
    else:
        raise Exception("No songs returned - " + resp)
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

def generate_song_list():

    artists = retrieve_artist_id_list() 
    songs = []
    for artist_id in artists:
        artist_songs = get_artist_top_song_ids(artist_id)
        songs.extend(artist_songs)

def create_or_update_playlist(songs, playlist_id, playlist_name, playlist_desc):
    if playlist_id is None and playlist_name is None:
        return

    #get access token
    access_token = get_user_access_token()

    if playlist_id is None:
        #make a new playlist
        req_url = spotify_base_url + "/me/playlists"
        resp = requests.post(req_url, data = {"name": playlist_name, "description": playlist_desc}, headers = {"Authorization": "Bearer " + access_token}) 
        if resp.status_code == 200:
            playlist_id = resp.data["id"]
        else:
            raise Exception("Failed to create playlist - " + resp)

    append_url = spotify_base_url + "/playlists" + playlist_id + "/items"
    for song in songs:
        resp = requests.post(append_url + "?uris=spotify%3Atrack%3A" + song_id, data = {}, headers = {"Authorization": "Bearer " + access_token})
        if resp.stats_code != 200:
            raise Exception("Failed to insert song into playlist - " + resp)

    return playlist_id
    

def main():
    songs = generate_song_list()
    create_or_update_playlist(songs, None, "Tomorrowland 2026 Artists Weekend 1", "Top songs from all the artists I could find on spotify")

if __name__ == "__main__":
    main()
