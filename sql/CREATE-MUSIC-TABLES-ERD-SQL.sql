DROP DATABASE IF EXISTS datamining_itc_music;
CREATE DATABASE IF NOT EXISTS datamining_itc_music;

USE datamining_itc_music;

CREATE TABLE `Track` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `title` varchar(255),
  `duration` int,
  `album_id` int
);

CREATE TABLE `Album` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `year` datetime,
  `name` varchar(255)
);

CREATE TABLE `Artist` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255)
);

CREATE TABLE `AlbumArtist` (
  `artist_id` int,
  `album_id` int
);

CREATE TABLE `Genre` (
  `id` int8 PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255)
);

CREATE TABLE `GenreAlbum` (
  `album_id` int,
  `genre_id` int8
);

ALTER TABLE `GenreAlbum` ADD FOREIGN KEY (`album_id`) REFERENCES `Album` (`id`);

ALTER TABLE `GenreAlbum` ADD FOREIGN KEY (`genre_id`) REFERENCES `Genre` (`id`);

ALTER TABLE `Track` ADD FOREIGN KEY (`album_id`) REFERENCES `Album` (`id`);

ALTER TABLE `AlbumArtist` ADD FOREIGN KEY (`artist_id`) REFERENCES `Artist` (`id`);

ALTER TABLE `AlbumArtist` ADD FOREIGN KEY (`album_id`) REFERENCES `Album` (`id`);