import grequests
import logging
from bs4 import BeautifulSoup


class Scraper:
    BASE_URL = "https://www.discogs.com/"
    BASE_OPTIONS = "search/?limit=250&sort=have%2Cdesc&ev=em_rs&type=master&layout=sm"

    URL = BASE_URL + BASE_OPTIONS

    def __init__(self, count: int, year: int = None):
        """
        Scraping class for Discogs.
        Args:
            count (int): number of pages to request
            year (int): year to filter
        """
        self.Logger = logging.getLogger(__name__)
        self.count = count
        self.year = year
        self.albums = []

    def scrape_album_pages(self):
        """
        Scrape album pages on Discogs with the options given in the class constructor.
        """
        requests_results = self.request_albums()
        for result in requests_results:
            self.Logger.debug(f"Scraping {result.url}")
            html_doc = result.text
            self.scrape_page(html_doc)

    def scrape_page(self, html_page: str):
        """
        Requests and scrapes the given discogs url
        Args:
            html_page: discogs html page to scrape
        """
        soup = BeautifulSoup(html_page, features="html.parser")
        cards_layout = soup.find("ul", {"class": "cards cards_layout_text-only"})
        soup_cards = BeautifulSoup(str(cards_layout), features="html.parser")
        cards = soup_cards.find_all("div", {"class": "card_body"})

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
            self.albums.append(album)

        self.log_results()

    def request_albums(self):
        """
        Requests albums pages on discogs.
        Returns:
            list: htmls of pages to scrape
        """
        year_param = f"&year={self.year}" if self.year else ""
        url = self.URL + year_param
        pages = [f"&page={page}" for page in range(1, self.count + 1)]
        rs = (grequests.get(url + page) for page in pages)
        self.Logger.info(f"Requesting first {self.count} pages")
        requests_results = grequests.map(rs)
        return requests_results

    def log_results(self):
        """
        Prints the scraped artists - albums
        """
        for album in self.albums:
            self.Logger.debug(f"{album['artist']['name']} - {album['name']}")
