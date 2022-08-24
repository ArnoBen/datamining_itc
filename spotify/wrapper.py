import json
import logging
import os
import threading
import time

import dotenv
import requests

from spotify import SpotifyAuth

dotenv.load_dotenv()


class SpotifyWrapper:
    BASE_URL = 'https://api.spotify.com/v1/'

    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.auth = SpotifyAuth(os.environ['CLIENT_ID'], os.environ['CLIENT_SECRET'])
        self.headers = self.auth.get_headers()
        self._start_auth_token_refresh()

    def search(self, query: str):
        """Searches spotify with the given query"""
        params = {'q': query, 'limit': 1, 'type': 'track'}
        result = requests.get(self.BASE_URL + 'search', headers=self.headers, params=params)
        try:
            data = json.loads(result.text)
            if 'error' in data:
                self.logger.warning(f"Error {data['error']['status']} for query {query}")
                if data['error']['status'] == 401:  # 401: token expired
                    # Request new access tokens
                    self.headers = self.auth.get_headers()
                    self.logger.info('Refreshing access token.')
                    return self.search(query)
                return None
            else:
                if len(data['tracks']['items']) > 0:
                    track = data['tracks']['items'][0]
                    return track
                else:
                    return None
        except json.decoder.JSONDecodeError as e:
            self.logger.error('Error occured when opening spotify search query result:', e)
            return None

    def get_audio_features(self, track_ids: list):
        """Gets the audio features of a list of songs from spotify's api"""
        params = {'ids': ','.join(track_ids)}
        result = requests.get(self.BASE_URL + 'audio-features', headers=self.headers, params=params)
        data = json.loads(result.text)
        return data['audio_features']

    def _start_auth_token_refresh(self):
        """Starts a thread to periodically refresh tokens"""
        refresh_token_thread = threading.Thread(target=self._refresh_auth_token_periodically)
        refresh_token_thread.setDaemon(True)
        refresh_token_thread.start()

    def _refresh_auth_token_periodically(self):
        """Queries for a new access token to prevent expiration"""
        while True:
            time.sleep(3500)
            self.logger.debug('Refreshing access token.')
            self.headers = self.auth.get_headers()


if __name__ == '__main__':
    spotify_wrapper = SpotifyWrapper()
    search_result = spotify_wrapper.search("Touch daft punk")

    features = spotify_wrapper.get_audio_features(search_result['id'])['audio_features']
    print(features)
    print("Song tempo:", int(features[0]['tempo']))