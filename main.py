#!/usr/bin/python3.9
# -*- coding: utf-8 -*-

import logging
import argparse
from scraping import Scraper


def parse_arguments():
    """
    Parse the cli arguments given by the user.
    Returns:
        parser: parser object containing arguments and their values
    """
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", required=False, action="store_true", default=False,
                        help="set log level to debug")
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
    log_level = logging.DEBUG if args.pop("debug") else logging.INFO
    logging.basicConfig(level=log_level, format='%(asctime)s %(levelname)s:%(message)s')

    save = args.pop("save")  # bool that we will use when we implement the storage in db
    scraper = Scraper(**args)
    scraper.scrape_album_pages()


if __name__ == "__main__":
    main()
