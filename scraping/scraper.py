import logging
import itertools

import grequests
from bs4 import BeautifulSoup
from utils import minutes_sec_2_sec


class Scraper:
    BASE_URL = "https://www.discogs.com"
    BASE_OPTIONS = "/search/?limit=50&sort=have%2Cdesc&ev=em_rs&type=master&layout=sm"
    URL = BASE_URL + BASE_OPTIONS
    BATCH_SIZE = 50

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

    def scrape_albums(self):
        """
        Scrape album pages on Discogs with the options given in the class constructor.
        """
        albums = []
        requests_results = self._request_albums()
        for i, result in enumerate(requests_results):
            self.Logger.info(f"Scraping page {i + 1}/{len(requests_results)}: {result.url}")
            albums_page = self._scrape_albums_page(result.text)
            for album in albums_page:
                albums.append(album)
        return albums

    @staticmethod
    def _scrape_albums_page(html_page: str):
        """
        Requests and scrapes the given discogs url
        Args:
            html_page: discogs html page to scrape
        """
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

    def scrape_albums_songs(self, albums: list):
        albums_data = []
        urls = (self.BASE_URL + album["url"] for album in albums)
        # Batching by groups of 10 requests:
        while True:
            batch = list(itertools.islice(urls, self.BATCH_SIZE))
            if not batch:
                break
            requests_results = self._request_albums_songs(batch)
            for result in requests_results:
                self.Logger.info(f"Scraping album {len(albums_data) + 1}/{len(albums)}: {result.url}")
                album_data = self._scrape_albums_songs_page(result.text)
                albums_data.append(album_data)

        # Creating a new album dict with more information:
        albums_complete = []
        for album, album_data in zip(albums, albums_data):
            full_data = {
                'name': album['name'],
                'artist': album['artist'],
                'url': album['url'],
                'genre': album_data['genre'],
                'year': album_data['year'],
                'tracks': album_data['tracks'],
            }
            albums_complete.append(full_data)
        return albums_complete

    @staticmethod
    def _scrape_albums_songs_page(html_page: str):
        soup = BeautifulSoup(html_page, features="html.parser")
        info = soup.find("tbody").find_all("th")
        genre = info[0].find_next_sibling().text
        year = info[2].find_next_sibling().text

        tracklist = soup.find("section", {"id": "release-tracklist"}).find_all("tr",attrs={'data-track-position': True})
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

    def _request_albums(self):
        """
        Requests albums pages on discogs.
        Returns:
            list: htmls of pages to scrape
        """
        log_str = f"Requesting the first {self.count} pages of albums"
        if self.year:
            log_str += f" released in {self.year}"
        self.Logger.info(log_str)
        year_param = f"&year={self.year}" if self.year else ""
        base = self.URL + year_param
        pages = [f"&page={page}" for page in range(1, self.count + 1)]
        rs = (grequests.get(base + page) for page in pages)
        requests_results = grequests.map(rs)
        return requests_results

    @staticmethod
    def _request_albums_songs(urls: list):
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
        rs = (grequests.get(url) for url in urls)
        requests_results = grequests.map(rs)
        return requests_results


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

