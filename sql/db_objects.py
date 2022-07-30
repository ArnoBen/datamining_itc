from utils import hash_tuple


class DbAlbum:
    def __init__(self, name: str, year: int, artist_name: str, n_tracks: int):
        self.name = name
        self.year = year
        self.id = hash_tuple((name.lower(), year, artist_name.lower(), n_tracks))


class DbArtist:
    def __init__(self, name: str):
        self.name = name
        self.id = hash_tuple((name.lower()))


class DbGenre:
    def __init__(self, name: str):
        self.name = name
        self.id = hash_tuple((name.lower()))


class DbTrack:
    def __init__(self, title: str, duration: int, album_id: str):
        self.title = title
        self.duration = duration
        self.album_id = album_id
        self.id = hash_tuple((title.lower(), duration, album_id))


# Join tables
class DbAlbumArtist:
    def __init__(self, album_id, artist_id):
        self.album_id = album_id
        self.artist_id = artist_id


class DbGenreAlbum:
    def __init__(self, genre_id, album_id):
        self.genre_id = genre_id
        self.album_id = album_id
