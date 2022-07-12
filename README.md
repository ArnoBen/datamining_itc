# Datamining @ ITC
Datamining and webscraping project where we will perform webscraping on Discogs and use Spotify's API to build a music themed database.

[GitHub link](https://github.com/ArnoBen/datamining_itc)
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

:warning: This will NOT work without the environment variables `CLIENT_ID` and `CLIENT_SECRET` required to 
request Spotify's API. The .env file will be provided in the .zip submission.

- Run `python server.py` 
- Go to http://127.0.0.1:5000/
- Enter a Spotify search

We do not have defined a definite use for Spotify's API but it's good to have it available.