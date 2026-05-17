from .rss import fetch_rss_articles
from .base import Article

FEED_URL = "https://carbon-herald.com/feed/"


def get_articles() -> list[Article]:
    try:
        return fetch_rss_articles(FEED_URL)
    except Exception:
        return []
