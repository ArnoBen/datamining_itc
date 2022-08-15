import requests
from spotify import SpotifyAuth
import os
import dotenv
import json
dotenv.load_dotenv()


class SpotifyWrapper:
    BASE_URL = 'https://api.spotify.com/v1/'

    def __init__(self):
        self.auth = SpotifyAuth(os.environ['CLIENT_ID'], os.environ['CLIENT_SECRET'])
        self.headers = self.auth.get_headers()

    def search(self, query: str):
        """Searches spotify with the given query"""
        params = {'q': query, 'limit': 1, 'type': 'track'}
        result = requests.get(self.BASE_URL + 'search', headers=self.headers, params=params)
        data = json.loads(result.text)
        track = data['tracks']['items'][0]
        return track

    def get_audio_features(self, track_ids: list):
        """Gets the audio features of a list of songs from spotify's api"""
        params = {'ids': ','.join(track_ids)}
        result = requests.get(self.BASE_URL + 'audio-features', headers=self.headers, params=params)
        data = json.loads(result.text)
        return data['audio_features']


if __name__ == '__main__':
    spotify_wrapper = SpotifyWrapper()
    search_result = spotify_wrapper.search("Touch daft punk")

    features = spotify_wrapper.get_audio_features(search_result['id'])['audio_features']
    print(features)
    print("Song tempo:", int(features[0]['tempo']))