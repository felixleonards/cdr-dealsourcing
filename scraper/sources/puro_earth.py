from playwright.sync_api import sync_playwright
from .base import Article

PROJECT_LIST_URL = "https://puro.earth/marketplace"
MAX_PROJECTS = 20


def get_articles() -> list[Article]:
    articles: list[Article] = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(PROJECT_LIST_URL, wait_until="networkidle", timeout=30000)
            links: list[str] = page.eval_on_selector_all(
                "a[href*='/projects/']",
                "els => [...new Set(els.map(e => e.href))]",
            )
            for url in links[:MAX_PROJECTS]:
                try:
                    page.goto(url, wait_until="networkidle", timeout=30000)
                    text = page.inner_text("body")
                    articles.append(Article(url=url, text=text))
                except Exception:
                    continue
            browser.close()
    except Exception:
        pass
    return articles
