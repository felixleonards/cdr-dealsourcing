import requests
from bs4 import BeautifulSoup
from .base import Article

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CDRScraper/1.0)"}
BUSINESS_WIRE_URL = "https://www.businesswire.com/news/home/search/?rpc=832&query={query}"
SEARCH_QUERIES = ["carbon+removal+cement", "CDR+cement", "carbon+dioxide+removal+cement"]


def get_articles() -> list[Article]:
    seen_links: set[str] = set()
    articles: list[Article] = []

    for query in SEARCH_QUERIES:
        url = BUSINESS_WIRE_URL.format(query=query)
        try:
            resp = requests.get(url, timeout=15, headers=HEADERS)
            resp.raise_for_status()
        except Exception:
            continue

        soup = BeautifulSoup(resp.text, "lxml")
        for a in soup.select("a.bwTitleLink"):
            href = a.get("href", "")
            if not href:
                continue
            full_url = f"https://www.businesswire.com{href}" if href.startswith("/") else href
            if full_url in seen_links:
                continue
            seen_links.add(full_url)
            try:
                article_resp = requests.get(full_url, timeout=15, headers=HEADERS)
                article_resp.raise_for_status()
                article_soup = BeautifulSoup(article_resp.text, "lxml")
                text = article_soup.get_text(separator=" ", strip=True)
                articles.append(Article(url=full_url, text=text))
            except Exception:
                continue

    return articles
