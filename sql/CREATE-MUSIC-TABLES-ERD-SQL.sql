CREATE DATABASE IF NOT EXISTS datamining_itc_music ;

USE datamining_itc_music;

CREATE TABLE `Song` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `title` varchar(255),
  `album_id` int,
  `songtime` int
);

CREATE TABLE `Album` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `year` datetime,
  `name` varchar(255)
);

CREATE TABLE `Artist` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `first_name` varchar(255),
  `last_name` varchar(255),
  `nickname` varchar(255),
  `description` varchar(255)
);

CREATE TABLE `AlbumArtist` (
  `artist_id` int,
  `album_id` int
);

CREATE TABLE `Genre` (
  `id` int PRIMARY KEY AUTO_INCREMENT,
  `name` varchar(255)
);

CREATE TABLE `GenreAlbum` (
  `album_id` int,
  `genre_id` int
);

ALTER TABLE `Song` ADD FOREIGN KEY (`album_id`) REFERENCES `Album` (`id`);

ALTER TABLE `AlbumArtist` ADD FOREIGN KEY (`artist_id`) REFERENCES `Artist` (`id`);

ALTER TABLE `AlbumArtist` ADD FOREIGN KEY (`album_id`) REFERENCES `Album` (`id`);

ALTER TABLE `GenreAlbum` ADD FOREIGN KEY (`album_id`) REFERENCES `Album` (`id`);

ALTER TABLE `GenreAlbum` ADD FOREIGN KEY (`genre_id`) REFERENCES `Genre` (`id`);
