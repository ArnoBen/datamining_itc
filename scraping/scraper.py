import itertools
import logging
import time
from multiprocessing import Pool
from queue import Queue
from threading import Thread

import grequests
from bs4 import BeautifulSoup
from tqdm import tqdm

from utils import minutes_sec_2_sec, requests_session
from utils.requests_session import get_session


class Scraper:
    BASE_URL = "https://www.discogs.com"
    BASE_OPTIONS = "/search/?limit=100&sort=have%2Cdesc&ev=em_rs&type=master&layout=sm"
    URL = BASE_URL + BASE_OPTIONS
    BATCH_SIZE = 100

    def __init__(self, count: int = 3, year: int = None, cores: int = 4):
        """
        Scraping class for Discogs.
        Args:
            count (int): number of pages to request
            year (int): year to filter
            cores (int): cpu cores to use for multiprocessing
        """
        self.Logger = logging.getLogger(__name__)
        self.count = count
        self.year = year
        self.errors = []
        self.n_cores = cores

    def scrape_albums(self):
        """
        Scrape album pages on Discogs with the options given in the class constructor.
        Returns:
            list: albums containing name, artist and url
        """
        albums = []
        responses = self._request_albums()
        for i, response in tqdm(enumerate(responses), total=len(responses)):
            html_page, url, status_code = response
            self.Logger.debug(f"Scraping page {i + 1}/{len(responses)}: {url}")
            albums_page = self._scrape_albums_page(response)
            for album in albums_page:
                albums.append(album)
        return albums

    def _scrape_albums_page(self, response: tuple):
        """
        Scrapes the given discogs page of album list
        Args:
            response (tuple): request response containing (html, url, status_code)
        """
        html_page, url, status_code = response
        try:
            if not html_page:
                raise ValueError(f"HTML page empty, request response code {status_code}")
            soup = BeautifulSoup(html_page, features="html.parser")
            cards_layout = soup.find("ul", {"class": "cards cards_layout_text-only"})
            soup_cards = BeautifulSoup(str(cards_layout), features="html.parser")
            cards = soup_cards.find_all("div", {"class": "card_body"})

            albums_page = []
            for card in cards:
                album_name = card.find("a", {"class": "search_result_title"}).text
                album_url = card.find("a", {"class": "search_result_title"}).attrs['href']
                album_artist = card.find("span", attrs={'title': True}).find("a")
                artist = {
                    "name": album_artist.text,
                    "url": album_artist.attrs['href'],
                }
                album = {
                    "name": album_name,
                    "artist": artist,
                    "url": album_url,
                }
                albums_page.append(album)

            return albums_page

        except Exception as e:
            self.Logger.error(f"\nAn error occurred when scraping page {url}: {e}")
            self.errors.append((url, e.__traceback__))

    def scrape_albums_songs(self, albums: list):
        """
        Scrapes each album's individual page
        Args:
            albums: list containing basic album information and their dedicated discogs url that will be scraped.

        Returns:
            list: albums containing name, artist, url, genre, year and tracklist
        """
        self.Logger.info(f"Scraping {len(albums)} albums")
        albums_data = []
        urls = (self.BASE_URL + album["url"] for album in albums)
        responses_queue = Queue()

        def download_pages(_urls, q):
            while True:
                batch = list(itertools.islice(_urls, self.BATCH_SIZE))
                if not batch:
                    break
                for response in self._request_albums_songs(batch): q.put(response)

        worker = Thread(target=download_pages, args=(urls, responses_queue))
        worker.setDaemon(True)
        worker.start()
        with tqdm(total=len(albums)) as pbar:
            while worker.is_alive() or not responses_queue.empty():
                # Batching processing
                while worker.is_alive():
                    # While the queue is filling, waits for the queue to have at least
                    # n_cores elements before pooling the processing (optimization)
                    if responses_queue.qsize() >= self.n_cores:
                        break
                    time.sleep(0.001)
                queue_batch = [responses_queue.get(block=True) for i in range(min(self.n_cores, responses_queue.qsize()))]
                with Pool(self.n_cores) as p:
                    for album_data in p.imap(self._scrape_albums_songs_page, queue_batch):
                        albums_data.append(album_data)
                        pbar.update()

        # Creating a new album dict with more information:
        albums_complete = []
        for album, album_data in zip(albums, albums_data):
            if album_data is None:  # Happens when an error occurred during a request
                self.Logger.warning(f"\nIgnoring empty album_data for {album.get('url', None)}")
                continue
            full_data = {
                'name': album.get('name', None),
                'artist': album.get('artist', None),
                'url': album.get('url', None),
                'genre': album_data.get('genre', None),
                'year': album_data.get('year', None),
                'tracks': album_data.get('tracks', None),
            }
            albums_complete.append(full_data)
        return albums_complete

    def _scrape_albums_songs_page(self, response: tuple):
        """
        Scrapes the given discogs page of an album
        Args:
            response (tuple): request response containing (html, url, status_code)
        """
        html_page, url, status_code = response
        try:
            self.Logger.debug(f"Scraping album : {url}")
            if not html_page:
                raise ValueError(f"HTML page empty, request response code {status_code}")
            soup = BeautifulSoup(html_page, features="html.parser")
            info = soup.find("tbody").find_all("th")
            genre = info[0].find_next_sibling().text
            year = info[2].find_next_sibling().text

            tracklist = soup.find("section", {"id": "release-tracklist"}).find_all("tr",
                                                                                   attrs={'data-track-position': True})
            tracks = []
            for track in tracklist:
                track_name = track.select('td[class*="trackTitle"]')[0].text
                track_duration = track.select('td[class*="duration"]')[0].text
                track_info = {
                    "name": track_name,
                    "duration": minutes_sec_2_sec(track_duration) if track_duration else None
                }
                tracks.append(track_info)

            album_data = {
                "genre": genre if genre else None,
                "year": int(year) if year else None,
                "tracks": tracks,
            }
            return album_data

        except Exception as e:
            print("\n")
            self.Logger.error(f"\nAn error occurred when scraping page {url}: {e}")
            self.errors.append((url, e.__traceback__))

    def _request_albums(self):
        """
        Requests albums pages on discogs.
        Returns:
            list: htmls of pages to scrape
        """
        self.Logger.info(f"Requesting the first {self.count} pages of albums" +
                         (f" released in {self.year}" if self.year else ""))
        year_param = f"&year={self.year}" if self.year else ""
        pages = [self.URL + year_param + f"&page={page}" for page in range(1, self.count + 1)]
        session = get_session()
        rs = (grequests.get(page, stream=False, session=session) for page in pages)
        responses = grequests.map(rs)
        for response in responses: response.close()
        return [(response.text, response.url, response.status_code) for response in responses]

    def _request_albums_songs(self, urls: list):
        """
        Requests album song pages on discogs.

        This is different from request albums:
         request_albums requests the page containing a list of albums
         request_album_songs requests specific album pages containing their list of songs.
        Args:
            urls: url of pages to request
        Returns:
            list: htmls of pages to scrape
        """
        self.Logger.debug(f"Requesting {len(urls)} album pages")
        session = requests_session.get_session()
        rs = (grequests.get(url, stream=False, session=session) for url in urls)
        responses = grequests.map(rs)
        for response in responses: response.close()
        return [(response.text, response.url, response.status_code) for response in responses]

    def print_errors(self):
        if self.errors:
            self.Logger.warning("These pages raised errors when scraping: ")
            for url in self.errors:
                self.Logger.warning(url)


if __name__ == "__main__":
    test_albums = [
        {
            'name': 'The Dark Side Of The Moon',
            'artist': {'name': 'Pink Floyd', 'url': '/artist/45467-Pink-Floyd'},
            'url': '/master/10362-Pink-Floyd-The-Dark-Side-Of-The-Moon'
        },
        {
            'name': "Sgt. Pepper's Lonely Hearts Club Band",
            'artist': {'name': 'The Beatles', 'url': '/artist/82730-The-Beatles'},
            'url': '/master/23934-The-Beatles-Sgt-Peppers-Lonely-Hearts-Club-Band'
        },
        {
            'name': 'Abbey Road',
            'artist': {'name': 'The Beatles', 'url': '/artist/82730-The-Beatles'},
            'url': '/master/24047-The-Beatles-Abbey-Road'
        }
    ]
    scraper = Scraper()
    scraper.scrape_albums_songs(test_albums)
