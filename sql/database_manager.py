import os

import pymysql
from dotenv import load_dotenv

from .db_objects import DbAlbum, DbArtist, DbTrack, DbGenre, DbAlbumArtist, DbGenreAlbum

load_dotenv()


class DatabaseManager:
    def __init__(self):
        self.connection = pymysql.connect(user=os.environ["MYSQL_USER"],
                                          password=os.environ["MYSQL_PASSWORD"],
                                          db="datamining_itc_music")
        self.cursor = self.connection.cursor()

    def insert_data_from_album(self, album_dict: dict):
        """
        Inserts an album in the database
        Args:
            album_dict (dict): dictionary containing the album data
        """
        db_data = self._extract_album_data(album_dict)
        self._insert_album(db_data["album"])
        self._insert_artist(db_data["artist"])
        self._insert_genre(db_data["genre"])
        self._insert_tracks(db_data["tracks"])
        self._insert_album_artist(db_data["album_artist"])
        self._insert_genre_album(db_data["genre_album"])
        self.connection.commit()

    def get_tracks(self, size=None):
        """
        Gets tracks from the database
        Args:
            size: Applies a limit to the result. Returns all the database if none.

        Returns:
            tuple(tuple): Tracks information including artist and album

        """
        query = """
        SELECT t.id, t.title, t.tempo, a.name, a2.name 
        FROM Track t
            JOIN Album a ON a.id = t.album_id
            JOIN AlbumArtist aa on aa.album_id = a.id 
            JOIN Artist a2 on a2.id = aa.artist_id 
        """
        if size :
            query += f" LIMIT {size}"
        self.cursor.execute(query)
        result = self.cursor.fetchall()
        return result

    def insert_data_from_spotify(self, track_id, tempo):
        """Fill the tempo column of given tracks in the database"""
        query = f"UPDATE Track SET tempo = {tempo} WHERE id = '{track_id}'"
        self.cursor.execute(query)

    def _insert_album(self, album: DbAlbum):
        """Inserts an album into the database"""
        if not self._already_exists("Album", album.id):
            query = "INSERT INTO Album VALUES (%s, %s, %s)"
            values = (album.id, album.year, album.name)
            self.cursor.execute(query, values)

    def _insert_artist(self, artist:  DbArtist):
        """Insert an artist into the database"""
        if not self._already_exists("Artist", artist.id):
            query = "INSERT INTO Artist VALUES (%s, %s)"
            values = (artist.id, artist.name)
            self.cursor.execute(query, values)

    def _insert_genre(self, genre: DbGenre):
        """Insert a genre into the database"""
        if not self._already_exists("Genre", genre.id):
            query = "INSERT INTO Genre VALUES (%s, %s)"
            values = (genre.id, genre.name)
            self.cursor.execute(query, values)

    def _insert_tracks(self, tracks: list[DbTrack]):
        """Insert a track list into the database"""
        query = "INSERT INTO Track VALUES (%s, %s, %s, %s, %s)"
        for db_track in tracks:
            if not self._already_exists("Track", db_track.id):
                value = (db_track.id, db_track.title[:255], db_track.duration, None, db_track.album_id)
                self.cursor.execute(query, value)

    def _insert_album_artist(self, album_artist: DbAlbumArtist):
        """Insert an album-artist join row into the database"""
        if not self._already_exists_join("AlbumArtist", "album_id", "artist_id",
                                         album_artist.album_id, album_artist.artist_id):
            query = "INSERT INTO AlbumArtist VALUES (%s, %s)"
            values = (album_artist.album_id, album_artist.artist_id)
            self.cursor.execute(query, values)

    def _insert_genre_album(self, genre_album: DbGenreAlbum):
        """Insert a genre-album join row into the database"""
        if not self._already_exists_join("GenreAlbum", "genre_id", "album_id",
                                         genre_album.genre_id, genre_album.album_id):
            query = "INSERT INTO GenreAlbum VALUES (%s, %s)"
            values = (genre_album.genre_id, genre_album.album_id)
            self.cursor.execute(query, values)

    def _already_exists(self, table_name: str, checked_id: str):
        """
        Checks if a row already exists
        Args:
            table_name: table to search
            checked_id: id to check

        Returns:
            bool: Whether the row exists or not

        """
        query = f"SELECT id FROM {table_name} WHERE id = '{checked_id}'"
        self.cursor.execute(query)
        return len(self.cursor.fetchall()) > 0

    def _already_exists_join(self, table_name: str, col1: str, col2: str, id1: str, id2: str):
        """
        Checks if a row already exists in a join table between two elements
        Args:
            table_name: table to search
            col1: name of first column
            col2: name of second column
            id1: id of first element
            id2: id of second element

        Returns:
            bool: Whether the row exists or not
        """
        query = f"SELECT {col1}, {col2} FROM {table_name} WHERE {col1} = '{id1}' and {col2} = '{id2}'"
        self.cursor.execute(query)
        return len(self.cursor.fetchall()) > 0

    @staticmethod
    def _extract_album_data(album_dict: dict):
        """
        Creates instances of database objects that will make the db _insertion easier
        Args:
            album_dict (dict): dictionary containing the following data:
                'name': str
                'artist': str
                'url': str
                'genre': str
                'year': int
                'tracks': list of dict {name (str), duration (int)}
        Return:
            dict: Dictionary containing objects convenient for db formatting
        """

        db_album = DbAlbum(album_dict["name"],
                           album_dict["year"],
                           album_dict["artist"]["name"],
                           len(album_dict["tracks"]))
        db_artist = DbArtist(album_dict["artist"]["name"])
        db_tracks = [DbTrack(track["name"], track["duration"], db_album.id) for track in album_dict["tracks"]]
        db_genre = DbGenre(album_dict["genre"])
        db_album_artist = DbAlbumArtist(db_album.id, db_artist.id)
        db_genre_album = DbGenreAlbum(db_genre.id, db_album.id)

        db_data = {
            "album": db_album,
            "artist": db_artist,
            "tracks": db_tracks,
            "album_artist": db_album_artist,
            "genre": db_genre,
            "genre_album": db_genre_album
        }
        return db_data
