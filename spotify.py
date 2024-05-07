import time
import os
import pandas as pd
import numpy as np
import json
import matplotlib.pyplot as plt
import seaborn as sns
import random
from functools import reduce
import spotipy
import spotipy.util as util
from spotipy.oauth2 import SpotifyClientCredentials
from spotipy import oauth2
import csv
import lyricsgenius

# Authorization/ Authorization 
cid = ''
secret = ''
redirect_uri = ""
username = ''

# Authorization and sp to call the APIs
scope = 'user-top-read playlist-modify-private playlist-modify-public'
token = util.prompt_for_user_token(username, scope, client_id=cid, client_secret=secret, redirect_uri=redirect_uri)

if token:
    sp = spotipy.Spotify(auth=token)
else:
    print("Can't get token for", username)

playlist_link = "https://open.spotify.com/playlist/37i9dQZEVXbNG2KDcFcKOF?si=1333723a6eff4b7f&nd=1&dlsi=6ce05bd2564c4195"
playlist_URI = playlist_link.split("/")[-1].split("?")[0]
track_uris = [x["track"]["uri"] for x in sp.playlist_tracks(playlist_URI)["items"][:20]]  # Limiting to top 20 tracks

# Initialize Genius API
genius = lyricsgenius.Genius("gehQ281GDHsLX_LSk6IWVn5Y-Cb2H9Moa5YNXH3SS2Ol_hLcqqoYhcX6HLIShAbRFE6P8ieauLhqEKLw9JamJQ")

# Columns for the DataFrame
columns = ["Track", "Artist", "Popularity", "Genres", "Lyrics", "Sentiment"]

# DataFrame to store the results
data = []

# Loop through top 20 tracks in the playlist
for track in sp.playlist_tracks(playlist_URI)["items"][:20]:
    # URI
    track_uri = track["track"]["uri"]

    # Track name
    track_name = track["track"]["name"]

    # Main Artist
    artist_uri = track["track"]["artists"][0]["uri"]
    artist_info = sp.artist(artist_uri)

    # Name, popularity, genre
    artist_name = track["track"]["artists"][0]["name"]
    artist_pop = artist_info["popularity"]
    artist_genres = artist_info["genres"]

    # Album
    album = track["track"]["album"]["name"]

    # Popularity of the track
    track_pop = track["track"]["popularity"]

    # Get lyrics
    song = genius.search_song(track_name, artist_name)
    if song is not None:
        lyrics = song.lyrics
        # Perform Sentiment Analysis using TextBlob API tool to analyze text
        from textblob import TextBlob
        analysis = TextBlob(lyrics)
        sentiment = analysis.sentiment.polarity
    else:
        lyrics = "Lyrics not found"
        sentiment = None

    # Append the data to the list
    data.append([track_name, artist_name, artist_pop, artist_genres, lyrics, sentiment])

# Create DataFrame from the list
df = pd.DataFrame(data, columns=columns)

# Save the DataFrame to a CSV file
df.to_csv("playlist_song_analysis.csv", index=False)
print("Sentiment Analysis completed and saved to playlist_song_analysis.csv")

# Plotting sentiment analysis
plt.figure(figsize=(10, 6))
sns.barplot(x='Track', y='Sentiment', data=df, palette='coolwarm')
plt.title('Sentiment Analysis of Top 20 Songs')
plt.xlabel('Track')
plt.ylabel('Sentiment Polarity')
plt.xticks(rotation=90)
plt.tight_layout()
plt.show()
