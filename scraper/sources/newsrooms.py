import requests
from bs4 import BeautifulSoup
from .base import Article

HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; CDRScraper/1.0)"}
MAX_ARTICLES_PER_NEWSROOM = 10

NEWSROOMS = [
    ("Heidelberg Materials", "https://www.heidelbergmaterials.com/en/media/press-releases"),
    ("Holcim", "https://www.holcim.com/media/press-releases"),
]


def get_articles() -> list[Article]:
    articles: list[Article] = []
    for _company, newsroom_url in NEWSROOMS:
        domain = "https://" + newsroom_url.split("/")[2]
        try:
            resp = requests.get(newsroom_url, timeout=15, headers=HEADERS)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "lxml")
            seen: set[str] = set()
            links = [
                a["href"] for a in soup.find_all("a", href=True)
                if any(kw in a["href"].lower() for kw in ("press", "news", "release", "media"))
            ]
            for href in links[:MAX_ARTICLES_PER_NEWSROOM]:
                full_url = href if href.startswith("http") else f"{domain}{href}"
                if full_url in seen:
                    continue
                seen.add(full_url)
                try:
                    pr_resp = requests.get(full_url, timeout=15, headers=HEADERS)
                    pr_resp.raise_for_status()
                    pr_soup = BeautifulSoup(pr_resp.text, "lxml")
                    text = pr_soup.get_text(separator=" ", strip=True)
                    articles.append(Article(url=full_url, text=text))
                except Exception:
                    continue
        except Exception:
            continue
    return articles
