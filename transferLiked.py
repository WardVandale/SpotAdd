import os
import json
import spotipy
import sys
import time
from spotipy.oauth2 import SpotifyOAuth
from datetime import datetime

# Initialize isAdded to False and previous track URI to None
isAdded = False
previous_track_uri = None

def saveCreds():
    print("apicreds.json does not exist, creating...")
    clientId = input("client id: ")
    clientSecret = input("client secret: ")
    username = input("username: ")

    creds = {
        "clientId": clientId,
        "clientSecret": clientSecret,
        "username": username
    }
    with open('apicreds.json', 'w') as outfile:
        json.dump(creds, outfile)
    print("Saved credentials in apicreds.json")

def getCreds():
    file_exists = os.path.exists("apicreds.json")
    if not file_exists:
        saveCreds()
    with open('apicreds.json') as infile:
        return json.load(infile)

creds = getCreds()

client_id = creds["clientId"]
client_secret = creds["clientSecret"]

scopes = [
    'playlist-read-private',
    'playlist-read-collaborative',
    'user-read-playback-state',
    'user-read-currently-playing',
    'playlist-modify-public',
    'playlist-modify-private',
    'user-library-read',  # added scope for reading liked songs
]

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri='http://127.0.0.1:8888/callback', scope=scopes))

# Function to create a new playlist with the given name
def create_playlist(name):
    user_id = sp.me()['id']
    playlist = sp.user_playlist_create(user_id, name, public=False)
    return playlist['id']

# Function to get IDs of all liked songs
def get_liked_songs():
    liked_songs = []
    results = sp.current_user_saved_tracks()
    while results:
        for item in results['items']:
            track = item['track']
            liked_songs.append(track['id'])
        if results['next']:
            results = sp.next(results)
        else:
            results = None
    return liked_songs

# Function to add songs to a playlist given its ID
# Function to add songs to a playlist given its ID
def add_songs_to_playlist(playlist_id, song_ids):
    # Split song_ids into chunks of 100
    chunks = [song_ids[i:i + 100] for i in range(0, len(song_ids), 100)]
    
    # Add songs to the playlist sequentially in chunks
    for chunk in chunks:
        sp.playlist_add_items(playlist_id, chunk)


if __name__ == "__main__":
    currentDate = datetime.now().strftime("%Y-%m-%d")
    liked_songs = get_liked_songs()
    playlist_name = f"Liked Songs [{currentDate}]"
    playlist_id = create_playlist(playlist_name)
    add_songs_to_playlist(playlist_id, liked_songs)
    print(f"Playlist '{playlist_name}' created with your liked songs.")
