import os
import requests
import json

spotify_base_url = "https://api.spotify.com/v1"
client_id = os.environ['SPOTIFY_CLIENT_ID']
client_secret = os.environ['SPOTIFY_CLIENT_SECRET']

def get_access_token():

    auth_url = 'https://accounts.spotify.com/api/token'
    auth_headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    auth_body = 'grant_type=client_credentials&client_id=' + client_id + 'client_secret=' + client_secret

    auth_resp = requests.post(auth_url, data = auth_body, headers = auth_headers)
    
    if auth_resp.status_code == 200:
        return auth_resp.text.access_token

    else return None
    
def get_artist_top_song_ids(artist_id):
    access_token = get_access_token()

    url = spotify_base_url + "/artists?"
    resp = requests.get(url, headers = {"Authorization": "Bearer  " + access_token})
    songs = None
    if resp.status_code = 200:
        songs = resp.text
        song_ids = []

        for song in songs:
            song_ids.append(song["id"])

        return song_ids
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

def generate_song_list(playlist_id, playlist_name, playlist_desc):
    if playlist_id is None and playlist_name is None:
        return

    artists = retrieve_artist_id_list() 
    songs = []
    for id in artists:
        artist_songs = get_artist_top_song_ids(artist_id)
        songs.extend(artist_songs)

    if playlist_id is None:
        #make a new playlist
        req_url = spotify_base_url + "/me/playlists"
        #TODO auth flow
        resp = requests.post(req_url, data = {"name": playlist_name, "description": playlist_desc}, headers = {"jk"}) 
        if resp.status_code = 200:
            playlist_id = resp.data["id"]

    append_url = spotify_base_url + "/playlists" + playlist_id + "/items"
    for song in songs:
        #TODO auth flow
        resp = requests.post(append_url + "?uris=spotify%3Atrack%3A" + song_id, data = {}, headers = {})

    return playlist_id
    


