DROP DATABASE IF EXISTS arno_shai;
CREATE DATABASE IF NOT EXISTS arno_shai;

USE arno_shai;

CREATE TABLE `Track` (
  `id` varchar(255) PRIMARY KEY,
  `album_id` varchar(255),
  `title` varchar(255),
  `duration` int,
  `danceability` float,
  `energy` float,
  `loudness` float,
  `speechiness` float,
  `acousticness` float,
  `instrumentalness` float,
  `valence` float,
  `tempo` int
);

CREATE TABLE `Album` (
  `id` varchar(255) PRIMARY KEY,
  `year` int,
  `name` varchar(255)
);

CREATE TABLE `Artist` (
  `id` varchar(255) PRIMARY KEY,
  `name` varchar(255)
);

CREATE TABLE `AlbumArtist` (
  `album_id` varchar(255),
  `artist_id` varchar(255)
);

CREATE TABLE `Genre` (
  `id` varchar(255) PRIMARY KEY,
  `name` varchar(255)
);

CREATE TABLE `GenreAlbum` (
  `genre_id` varchar(255),
  `album_id` varchar(255)
);

ALTER TABLE `GenreAlbum` ADD FOREIGN KEY (`album_id`) REFERENCES `Album` (`id`);

ALTER TABLE `GenreAlbum` ADD FOREIGN KEY (`genre_id`) REFERENCES `Genre` (`id`);

ALTER TABLE `Track` ADD FOREIGN KEY (`album_id`) REFERENCES `Album` (`id`);

ALTER TABLE `AlbumArtist` ADD FOREIGN KEY (`artist_id`) REFERENCES `Artist` (`id`);

ALTER TABLE `AlbumArtist` ADD FOREIGN KEY (`album_id`) REFERENCES `Album` (`id`);
