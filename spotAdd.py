import os
import sys
import json
import spotipy
import time
from spotipy.oauth2 import SpotifyOAuth

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
]

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=client_id, client_secret=client_secret, redirect_uri='http://localhost:8888/callback', scope=scopes))

user_playlists = sp.current_user_playlists()
your_playlists = [playlist for playlist in user_playlists['items'] if playlist['owner']['id'] == sp.me()['id']]

print("Your Created Playlists:")
for i, playlist in enumerate(your_playlists):
    print(f"{i + 1}. {playlist['name']}")

selected_index = int(input("Enter the number of the playlist to add songs to: ")) - 1

if 0 <= selected_index < len(your_playlists):
    selected_playlist_id = your_playlists[selected_index]['id']
    stopProgram = 0
    while True:
        current_playback = sp.current_playback()
        if current_playback is not None:
            current_track_uri = current_playback['item']['uri']
            current_track_duration_ms = current_playback['item']['duration_ms']
            current_track_progress_ms = current_playback['progress_ms']

            remaining_playtime_seconds = (current_track_duration_ms - current_track_progress_ms) / 1000
            stopProgram = 0

            if previous_track_uri != current_track_uri:
                # New song started, reset isAdded to False
                isAdded = False
                previous_track_uri = current_track_uri

                # Check if the current track URI is already in the playlist
                playlist_tracks = sp.playlist_tracks(selected_playlist_id)
                track_uris_in_playlist = [track['track']['uri'] for track in playlist_tracks['items']]

                if current_track_uri in track_uris_in_playlist:
                    isAdded = True

            if remaining_playtime_seconds <= 5 and not isAdded:
                playlist_tracks = sp.playlist_tracks(selected_playlist_id)
                track_uris_in_playlist = [track['track']['uri'] for track in playlist_tracks['items']]

                if current_track_uri not in track_uris_in_playlist:
                    sp.playlist_add_items(selected_playlist_id, [current_track_uri])
                    print(f"Added '{current_playback['item']['name']}' to the playlist.")
                    isAdded = True  # Mark the song as added
            else:
                pass
        else:
            stopProgram = stopProgram + 1
            if stopProgram == 600:
                sys.exit()
        time.sleep(1)
else:
    pass
