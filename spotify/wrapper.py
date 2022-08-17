import json
import logging
import os

import dotenv
import requests

from spotify import SpotifyAuth

dotenv.load_dotenv()


class SpotifyWrapper:
    BASE_URL = 'https://api.spotify.com/v1/'

    def __init__(self):
        self.auth = SpotifyAuth(os.environ['CLIENT_ID'], os.environ['CLIENT_SECRET'])
        self.headers = self.auth.get_headers()
        self.Logger = logging.Logger(__name__)

    def search(self, query: str):
        """Searches spotify with the given query"""
        params = {'q': query, 'limit': 1, 'type': 'track'}
        result = requests.get(self.BASE_URL + 'search', headers=self.headers, params=params)
        data = json.loads(result.text)
        if 'error' in data:
            logging.warning(f"Error {data['error']['status']} for query {query}")
            if data['error']['status'] == 401:  # 401: token expired
                # Request new access tokens
                self.headers = self.auth.get_headers()
                self.Logger.info('Requesting new access tokens')
                return self.search(query)
            return None
        else:
            if len(data['tracks']['items']) > 0:
                track = data['tracks']['items'][0]
                return track
            else:
                return None

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