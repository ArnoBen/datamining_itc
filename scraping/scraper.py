import logging
import itertools

import grequests
from multiprocessing import Pool
from tqdm import tqdm
from bs4 import BeautifulSoup

from utils.requests_session import get_session
from utils import minutes_sec_2_sec, requests_session


class Scraper:
    BASE_URL = "https://www.discogs.com"
    BASE_OPTIONS = "/search/?limit=50&sort=have%2Cdesc&ev=em_rs&type=master&layout=sm"
    URL = BASE_URL + BASE_OPTIONS
    BATCH_SIZE = 50
    PROCESSES = 8

    def __init__(self, count: int = 3, year: int = None):
        """
        Scraping class for Discogs.
        Args:
            count (int): number of pages to request
            year (int): year to filter
        """
        self.Logger = logging.getLogger(__name__)
        self.count = count
        self.year = year
        self.errors = []

    def scrape_albums(self):
        """
        Scrape album pages on Discogs with the options given in the class constructor.
        Returns:
            list: albums containing name, artist and url
        """
        albums = []
        responses = self._request_albums()
        for i, response in enumerate(responses):
            html_page, url, status_code = response
            self.Logger.info(f"Scraping page {i + 1}/{len(responses)}: {url}")
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
        albums_data = []
        urls = (self.BASE_URL + album["url"] for album in albums)

        while True:
            # Batching requests:
            batch = list(itertools.islice(urls, self.BATCH_SIZE))
            if not batch:
                break
            response = self._request_albums_songs(batch)
            # Scraping pages with multiprocessing for speed
            self.Logger.info(f"Scraping albums {len(albums_data) + len(batch)}/{len(albums)}")
            with Pool(self.PROCESSES) as p:
                album_data = list(
                    # Wrapping the multiprocessing in tqdm to show progress bar
                    tqdm(p.imap(self._scrape_albums_songs_page, response), total=len(batch))
                )
            albums_data += album_data
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
        self.Logger.info(f"Requesting {len(urls)} album pages")
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
