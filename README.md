# Datamining @ ITC

### [GitHub link](https://github.com/ArnoBen/datamining_itc)

Datamining and webscraping project where we will perform webscraping on Discogs and use Spotify's API to build a music themed database.

We are using [this Discogs page](https://www.discogs.com/search/?sort=have%2Cdesc&ev=em_rs&type=master)
which provides a table of albums-artists ranked by most popular of all time (called "Most Collected").

For now we are only scraping the pages. Afterwards, we will request the page for each album and scrap it as well.

We also registered to Spotify for Developers which provides a powerful API. 

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