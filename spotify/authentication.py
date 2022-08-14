import base64
import json
import logging
import os

import dotenv
import requests

dotenv.load_dotenv()


class SpotifyAuth:
    OAUTH_AUTHORIZE_URL = "https://accounts.spotify.com/authorize"
    OAUTH_TOKEN_URL = "https://accounts.spotify.com/api/token"

    def __init__(self, client_id, client_secret):
        self._client_id = client_id
        self._client_secret = client_secret
        self.access_token = self._get_access_token()

    def get_headers(self):
        headers = self._get_auth_header()
        headers["Content-Type"] = "application/json"
        return headers

    def _get_auth_header(self):
        token = self._get_access_token()
        return {"Authorization": "Bearer {0}".format(token)}

    def _get_access_token(self):
        payload = {"grant_type": "client_credentials"}
        headers = self._make_authorization_headers(
            self._client_id, self._client_secret
        )
        try:
            response = requests.post(
                self.OAUTH_TOKEN_URL,
                data=payload,
                headers=headers
            )
            token = json.loads(response.text)['access_token']
            return token

        except Exception as e:
            logging.error('Authentication token failed:', e)
            raise e

    @staticmethod
    def _make_authorization_headers(client_id, client_secret):
        auth_header = base64.b64encode((client_id + ":" + client_secret).encode('ascii'))
        return {"Authorization": f"Basic {auth_header.decode('ascii')}"}


if __name__ == '__main__':
    spot_auth = SpotifyAuth(client_id=os.environ['CLIENT_ID'], client_secret=os.environ['CLIENT_SECRET'])
    params = {'q': 'imagine dragons', 'limit': 1, 'offset': 0, 'type': 'track', 'market': None}
    headers = spot_auth.get_headers()
    result = requests.get('https://api.spotify.com/v1/search', headers=spot_auth.get_headers() ,params=params)
    data = json.loads(result.text)
    track = data['tracks']['items'][0]

    params_audiofeatures = {'ids': [track['id']]}
    result_audiofeatures = requests.get('https://api.spotify.com/v1/audio-features', headers=spot_auth.get_headers(), params=params_audiofeatures)

    print(json.loads(result_audiofeatures.text))