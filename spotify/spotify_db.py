import logging

from sql import DatabaseManager
from spotify import SpotifyWrapper


class SpotifyDBFiller:
    def __init__(self):
        self.dbmanager = DatabaseManager()
        self.wrapper = SpotifyWrapper()
        self.logger = logging.getLogger(__name__)

    def get_track_spotify_id(self, track_name: str, album: str, artist: str):
        """Search spotify to get the spotify's id of a given song"""
        try:
            track_data = self.wrapper.search(f"{track_name} {album} {artist}")
            if track_data:
                track_id = track_data['id']
                return track_id
            else:
                return None
        except ConnectionError as e:
            self.logger.error("Spotify search failed with error:", e)
            return None

    def get_audio_features(self, ids: list):
        """Gets the audio features of a list of songs from spotify's api"""
        feature_names = ['danceability', 'energy', 'loudness', 'speechiness',
                         'acousticness', 'instrumentalness', 'valence', 'tempo']
        try:
            return self.wrapper.get_audio_features(ids), feature_names
        except ConnectionError as e:
            self.logger.error("Spotify audio feature request failed with error:", e)
            return None, None

    def fill_audio_features_in_db(self, db_ids: list, features: list):
        """Fill the tempo column of given tracks in the database"""
        args = [tuple(feature + [db_id]) for feature, db_id in zip(features, db_ids)]
        self.dbmanager.insert_features_from_spotify(args)


if __name__ == "__main__":
    spotify = SpotifyDBFiller()
