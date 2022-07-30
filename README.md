# Datamining @ ITC

### [GitHub link](https://github.com/ArnoBen/datamining_itc)

Datamining and webscraping project where we will perform webscraping on Discogs and use Spotify's API to build a music themed database.

We are using [this Discogs page](https://www.discogs.com/search/?sort=have%2Cdesc&ev=em_rs&type=master)
which provides a table of albums-artists ranked by most popular of all time (called "Most Collected").

We also registered to Spotify for Developers which provides a powerful API.

## Versions

- Python (3.9.12)
- BeautifulSoup4 (4.11.1)
- spotipy (2.20.0)
- Flask (2.1.2) ~ out of scope but fun embedding
- grequests (0.6.0)
- python-dotenv (0.20.0)

## How to use

Using virtualenv:
 
0. virtualenv & activate
1. install the requirements.txt
2. `python3 main.py [-h] [-d] [-s] [-c COUNT] [-y YEAR] [-o CORES]`, see chapter below for more information.
3. `python3 spotify_server.py` # browser UI


:warning: You will need the environment variables `MYSQL_PASSWORD` and `MYSQL_USER` to connect to mysql database.
Moreover, you will need `CLIENT_ID` and `CLIENT_SECRET` to request Spotify's API. The .env file will be provided in the .zip submission.

### Scraping Discogs

```
usage: main.py [-h] [-d] [-s] [-c COUNT] [-y YEAR] [-o CORES]

optional arguments:
  -h, --help            show this help message and exit
  -d, --debug           set log level to debug
  -s, --save            save the scraped information in a database
  -c COUNT, --count COUNT
                        amount of pages to scrape (default: 3)
  -y YEAR, --year YEAR  year of album release to filter
  -o CORES, --cores CORES
                        Amount of CPU cores to use for multiprocessed scraping (default: 4)
```

This will scrape the albums pages in discogs starting from [this page](https://www.discogs.com/search/?limit=50&sort=have%2Cdesc&ev=em_rs&type=master&layout=sm)

### Database Architecture

![Database ERD](sql/ERD.png)
*Generated from https://dbdiagram.io/d/62e28addf31da965e832fdce*

To build the database tables, run:
```commandline
mysql -u root -p < sql/create_music_tables.sql
```

Or run the provided script `create_db.sh` in the sql folder.

#### Descriptions

- **Album**
    - id: album id (hash)
    - year: album release year
    - name: album name
- **Artist**
    - id: artist id (hash)
    - name: artist name. A band is considered an artist.
- **Genre**
  - id: genre id (hash)
  - name: genre name. If an album has multiple genres like "Rock/Blues", this is not split and is considered a single genre.
- **Track**
  - id: track id (hash)
  - title: track title
  - duration: track duration in seconds
  - album_id: album in which this track belongs
- **AlbumArtist**: Table joining Album with Artist
  - album_id: album id
  - artist_id: artist id
- **GenreAlbum** Table joining Genre with Album
  - genre_id: genre id
  - artist_id: artist id

Nb: The object's ids are obtained with a custom deterministic hash using hashlib.md5.

### Spotify queries

- Run `python spotify_server.py` 
- Go to http://127.0.0.1:5000/
- Enter a Spotify search

We do not have defined a definite use for Spotify's API but it's good to have it available.
