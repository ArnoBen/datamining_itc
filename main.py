import argparse
import logging
import time

from dotenv import load_dotenv
from tqdm import tqdm

from scraping import Scraper
from spotify import SpotifyDBFiller
from sql.database_manager import DatabaseManager

load_dotenv()


def parse_arguments():
    """
    Parse the cli arguments given by the user.
    Returns:
        parser: parser object containing arguments and their values
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", required=False, action="store_true", default=False,
                        help="set log level to debug")
    parser.add_argument("-s", "--save", required=False, action="store_true", default=False,
                        help="save the scraped information in a database")
    parser.add_argument("-c", "--count", required=False, type=int, default=3,
                        help="amount of pages to scrape (default: 3)")
    parser.add_argument("-y", "--year", required=False, type=int,
                        help="year of album release to filter")
    parser.add_argument("-o", "--cores", required=False, type=int, default=4,
                        help="amount of CPU cores to use for multiprocessed scraping (default: 4)")
    parser.add_argument("-a", "--api", required=False, action="store_true",
                        help="saves additional data from Spotify api")
    return parser


def scrape_discogs(args: dict):
    save = args.pop("save")  # bool that we will use when we implement the storage in db
    scraper = Scraper(**args)
    albums = scraper.scrape_albums()
    start_albums_scraping = time.time()
    albums = scraper.scrape_albums_songs(albums)
    logging.info(f"Scraped {len(albums)} albums containing a total of {sum(len(album['tracks']) for album in albums)} tracks.")
    logging.info(f"Album scraping completed in {time.time() - start_albums_scraping} seconds")
    scraper.print_errors()  # outputs urls of pages that raised an error during scraping
    if save:
        start_db_saving = time.time()
        logging.info("Saving data into database")
        dbmanager = DatabaseManager()
        for album in tqdm(albums, total=len(albums)):
            dbmanager.insert_data_from_album(album)
        logging.info(f"Database saving completed in {time.time() - start_db_saving} seconds.")


def fill_db_from_spotify(args):
    spotify = SpotifyDBFiller()
    tracks = spotify.get_tracks()
    db_ids, spotify_ids, tempos = [], [], []
    for track in tracks[:10]:
        db_id, name, album, artist = track
        db_ids.append(db_id)
        spotify_id = spotify.get_track_spotify_id(name, album, artist)
        spotify_ids.append(spotify_id)
        if len(spotify_ids) == 10:
            features = spotify.get_audio_features(spotify_ids)
            tempos = tempos + [int(feature['tempo']) for feature in features]
            spotify_ids = []
    spotify.fill_tempos_in_db(db_ids, tempos)


def main():
    start = time.time()
    parser = parse_arguments()
    args = vars(parser.parse_args())
    log_level = logging.DEBUG if args.pop("debug") else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s %(levelname)s:%(message)s')

    if args['api']:
        logging.info("Starting Spotify API requests")
        fill_db_from_spotify(args)
    else:
        del args['api']
        logging.info("Starting Discogs scraping")
        scrape_discogs(args)

    logging.info(f"Total process completed in {time.time() - start} seconds")


if __name__ == "__main__":
    main()
