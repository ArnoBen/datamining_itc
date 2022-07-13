import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from dotenv import load_dotenv
load_dotenv()

client_creds = SpotifyClientCredentials(client_id=os.environ["CLIENT_ID"], client_secret=os.environ["CLIENT_SECRET"])
sp = spotipy.Spotify(auth_manager=client_creds)


def search(query):
    response = sp.search(q=query, limit=20)
    result = []
    for idx, track in enumerate(response['tracks']['items']):
        item = {
            'idx': idx,
            'artist': track['artists'][0]['name'],
            'name': track['name'],
            'id': track['id'],
        }
        result.append(item)
    return result
