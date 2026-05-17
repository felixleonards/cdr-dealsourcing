import feedparser
import requests
from bs4 import BeautifulSoup
from .base import Article

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CDRScraper/1.0)"}


def fetch_rss_articles(feed_url: str) -> list[Article]:
    feed = feedparser.parse(feed_url)
    articles = []
    for entry in feed.entries:
        url = entry.get("link", "")
        if not url:
            continue
        try:
            resp = requests.get(url, timeout=15, headers=HEADERS)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")
            text = soup.get_text(separator=" ", strip=True)
            articles.append(Article(url=url, text=text))
        except Exception:
            continue
    return articles
