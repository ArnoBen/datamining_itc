#!/usr/bin/python3.9
# -*- coding: utf-8 -*-

import grequests
from bs4 import BeautifulSoup
import sys
import logging

logging.basicConfig(filename="discogs.log", level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')
Logger = logging.getLogger(__name__)

BASE_URL = "https://www.discogs.com/search/?sort=have%2Cdesc&ev=em_rs&type=master"


def print_results(artists, albums):
    """
    Prints the given artists - albums
    Args:
        artists: The artists list
        albums: The album list
    """
    for artist, album in zip(artists, albums):
        print(artist, "-", album)


def scrape_page(html_page: str):
    """
    Requests and scrapes the given discogs url
    Args:
        html_page: discogs html page to scrape
    """
    soup = BeautifulSoup(html_page, features="html.parser")
    cards_layout = soup.find("div", {"class": "cards cards_layout_large"})
    soup_cards = BeautifulSoup(str(cards_layout), features="html.parser")
    cards = soup_cards.find_all("div", {"class": "card card_large float_fix shortcut_navigable"})

    artists, albums = [], []
    for card in cards:
        album = card.find("a", {"class": "search_result_title"}).attrs["title"]
        artist = card.find("span", attrs={'title': True}).attrs['title']
        albums.append(album)
        artists.append(artist)

    print_results(artists, albums)


def request_first_pages(n_pages: int):
    """
    Requests the first n pages of albums
    Args:
        n_pages: number of pages to request
    """
    batch = [f"&page={page}" for page in range(1, n_pages + 1)]
    rs = (grequests.get(BASE_URL + url) for url in batch)
    Logger.info(f"Requesting first {n_pages} pages")
    requests_results = grequests.map(rs)
    for result in requests_results:
        Logger.info(f"Scraping {result.url}")
        html_doc = result.text
        scrape_page(html_doc)


def main():
    page_count = 3
    if len(sys.argv) == 1:
        print("Scraping 3 pages by default")
    elif len(sys.argv) == 2:
        page_count = int(sys.argv[1])
    elif len(sys.argv) > 2 or not sys.argv[1].isdigit():
        print("usage: ./discogs.py count")
        return

    request_first_pages(page_count)


if __name__ == "__main__":
    main()