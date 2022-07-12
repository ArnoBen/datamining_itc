# Datamining @ ITC
Datamining and webscraping project where we will perform webscraping on Discogs and use Spotify's API to build a music themed database.

## Packages used
- BeautifulSoup4 (4.11.1)
- spotipy (2.20.0)
- Flask (2.1.2) ~ out of scope but fun embedding

## How to use

### Scraping Discogs

Run `python discogs.py [count]`

The parameter "count" is the number of pages to be scraped.

This will display a list of Artist - Album scraped from the Discogs webpage.

### Spotify queries

- Run `python server.py` 
- Go to http://127.0.0.1:5000/
- Enter a Spotify search