# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from bs4 import BeautifulSoup
import requests


ALBUMS_URL = "https://www.discogs.com/search/?sort=have%2Cdesc&ev=em_rs&type=master"

html_doc = requests.get(ALBUMS_URL)
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
    
print(artists)
print(albums)
