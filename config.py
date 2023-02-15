from dataclasses import dataclass


@dataclass
class ScraperConfig:
    base_url: str = "https://www.discogs.com"
    base_options: str = "/search/?limit=100&sort=have%2Cdesc&ev=em_rs&type=master&layout=sm"
    batch_size: int = 100
