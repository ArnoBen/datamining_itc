import os

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()

client_creds = SpotifyClientCredentials(client_id=os.environ["CLIENT_ID"], client_secret=os.environ["CLIENT_SECRET"])
sp = spotipy.Spotify(auth_manager=client_creds)


def search(query: str):
    """
    Searches on Spotify
    Args:
        query (str): Terms to search

    Returns:
        list: Spotify query result
    """
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
