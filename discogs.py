#!/usr/bin/python3.9
# -*- coding: utf-8 -*-

import grequests
from bs4 import BeautifulSoup
import sys
import logging
import argparse

logging.basicConfig(filename="discogs.log", level=logging.DEBUG, format='%(asctime)s %(levelname)s:%(message)s')
Logger = logging.getLogger(__name__)

BASE_URL = "https://www.discogs.com/search/"
BASE_OPTIONS = "?limit=250?sort=have%2Cdesc&ev=em_rs&type=master&layout=sm"


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
    cards_layout = soup.find("ul", {"class": "cards cards_layout_text-only"})
    soup_cards = BeautifulSoup(str(cards_layout), features="html.parser")
    cards = soup_cards.find_all("div", {"class": "card_body"})

    artists, albums = [], []
    for card in cards:
        album = card.find("a", {"class": "search_result_title"}).text
        artist = card.find("span", attrs={'title': True}).attrs['title']
        albums.append(album)
        artists.append(artist)

    print_results(artists, albums)


def request_albums(count: int, year: int, verbose: bool):
    """
    Requests the first n pages of albums
    Args:
        count (int): number of pages to request
        year (int): year to filter
        verbose (bool): whereas to print more information
    """
    pages = [f"&page={page}" for page in range(1, count + 1)]
    year_param = f"&year={year}" if year else None
    rs = (grequests.get(BASE_URL + BASE_OPTIONS + page + year_param) for page in pages)
    Logger.info(f"Requesting first {count} pages")
    requests_results = grequests.map(rs)
    for result in requests_results:
        Logger.info(f"Scraping {result.url}")
        html_doc = result.text
        scrape_page(html_doc)


def parse_arguments():
    """
    Parse the cli arguments given by the user.
    Returns:
        parser: parser object containing arguments and their values
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", required=False, action="store_true", default=False,
                        help="outputs more information while scraping")
    parser.add_argument("-s", "--save", required=False, action="store_true", default=False,
                        help="save the scraped information in a database")
    parser.add_argument("-c", "--count", required=False, type=int, default=3,
                        help="amount of pages to scrape (default: 3) ")
    parser.add_argument("-y", "--year", required=False, type=int,
                        help="year of album release to filter")
    return parser


def main():
    parser = parse_arguments()
    args = vars(parser.parse_args())
    save = args.pop("save")  # bool that we will use when we implement the storage in db
    request_albums(**args)


if __name__ == "__main__":
    main()