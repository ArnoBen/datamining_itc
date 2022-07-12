#!/usr/bin/python3.9
# -*- coding: utf-8 -*-

from bs4 import BeautifulSoup
import requests
import sys


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


def scrape_page(url):
    """
    Requests and scrapes the given discogs url
    Args:
        url: discogs url to scrape
    """
    html_doc = requests.get(url)
    soup = BeautifulSoup(html_doc.text, features="html.parser")

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


def main():
    if len(sys.argv) == 1:
        print("Scraping 3 pages by default")
    elif len(sys.argv) > 2 or not sys.argv[1].isdigit():
        print("usage: ./discogs.py count")
        return

    page_count = int(sys.argv[1])

    for page in range(1, page_count + 1):
        ALBUMS_URL = BASE_URL + f"&page={page}"
        scrape_page(ALBUMS_URL)


if __name__ == "__main__":
    main()