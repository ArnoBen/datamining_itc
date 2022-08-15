from sql import DatabaseManager
from spotify import SpotifyWrapper


class SpotifyDBFiller:
    def __init__(self):
        self.dbmanager = DatabaseManager()
        self.wrapper = SpotifyWrapper()

    def get_track_spotify_id(self, track_name: str, album: str, artist: str):
        """Search spotify to get the spotify's id of a given song"""
        track_data = self.wrapper.search(f"{track_name} {album} {artist}")
        if track_data:
            track_id = track_data['id']
            return track_id
        else:
            return None

    def get_audio_features(self, ids: list):
        """Gets the audio features of a list of songs from spotify's api"""
        return self.wrapper.get_audio_features(ids)

    def fill_tempos_in_db(self, db_ids: list, tempos: list):
        """Fill the tempo column of given tracks in the database"""
        args = list(zip(tempos, db_ids))
        self.dbmanager.insert_tempo_list_from_spotify(args)


if __name__ == "__main__":
    spotify = SpotifyDBFiller()
