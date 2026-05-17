import requests
from bs4 import BeautifulSoup
from .base import Article

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CDRScraper/1.0)"}
BASE_URL = "https://www.carbonfuture.earth"
REGISTRY_URL = f"{BASE_URL}/registry"


def get_articles() -> list[Article]:
    articles: list[Article] = []
    try:
        resp = requests.get(REGISTRY_URL, timeout=15, headers=HEADERS)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        seen: set[str] = set()
        for a in soup.select("a[href*='/registry/']"):
            href = a.get("href", "")
            if not href or href in ("/registry", "/registry/"):
                continue
            full_url = f"{BASE_URL}{href}" if href.startswith("/") else href
            if full_url in seen:
                continue
            seen.add(full_url)
            try:
                proj_resp = requests.get(full_url, timeout=15, headers=HEADERS)
                proj_resp.raise_for_status()
                proj_soup = BeautifulSoup(proj_resp.text, "lxml")
                text = proj_soup.get_text(separator=" ", strip=True)
                articles.append(Article(url=full_url, text=text))
            except Exception:
                continue
    except Exception:
        pass
    return articles
