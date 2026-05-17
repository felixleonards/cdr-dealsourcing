import re

import requests
from bs4 import BeautifulSoup

from .rss import fetch_rss_articles
from .base import Article

FEED_URL = "https://carbon-herald.com/feed/"
HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CDR-DealSourcing/1.0)"}
MAX_ARCHIVE_PAGES = 30


def get_articles() -> list[Article]:
    try:
        return fetch_rss_articles(FEED_URL)
    except Exception:
        return []


def get_archive_articles() -> list[Article]:
    """Scrape paginated Carbon Herald archive for historical articles."""
    seen: set[str] = set()
    articles: list[Article] = []
    for page_num in range(1, MAX_ARCHIVE_PAGES + 1):
        if page_num == 1:
            url = "https://carbon-herald.com/"
        else:
            url = f"https://carbon-herald.com/page/{page_num}/"
        try:
            resp = requests.get(url, timeout=15, headers=HEADERS)
            if resp.status_code == 404:
                break  # no more pages
            resp.raise_for_status()
        except Exception:
            continue
        soup = BeautifulSoup(resp.text, "lxml")
        # Find article links — URLs that look like dated WordPress posts
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if not href.startswith("https://carbon-herald.com/"):
                continue
            # Skip category, tag, author, page links
            if any(skip in href for skip in ["/category/", "/tag/", "/author/", "/page/", "feed", "#"]):
                continue
            # Only dated article paths (contain a 4-digit year)
            if not re.search(r'/20\d{2}/', href):
                continue
            if href in seen:
                continue
            seen.add(href)
            try:
                art_resp = requests.get(href, timeout=15, headers=HEADERS)
                art_resp.raise_for_status()
                art_soup = BeautifulSoup(art_resp.text, "lxml")
                text = art_soup.get_text(separator=" ", strip=True)
                articles.append(Article(url=href, text=text))
            except Exception:
                continue
    return articles
