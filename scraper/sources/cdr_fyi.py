from playwright.sync_api import sync_playwright

from .base import Article

BASE_URL = "https://www.cdr.fyi"
MAX_ENTRIES = 50  # limit to avoid very long runs


def get_articles() -> list[Article]:
    articles: list[Article] = []
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch()
            page = browser.new_page()
            page.goto(BASE_URL, wait_until="networkidle", timeout=30000)

            # Collect links from both Purchasers and Suppliers tabs
            all_links: list[str] = []
            for tab_text in ["Purchasers", "Suppliers"]:
                try:
                    page.get_by_role("tab", name=tab_text).click()
                    page.wait_for_timeout(2000)
                    links = page.eval_on_selector_all(
                        "a[href*='/purchaser/'], a[href*='/supplier/']",
                        "els => [...new Set(els.map(e => e.href))]",
                    )
                    all_links.extend(links)
                except Exception:
                    continue

            seen: set[str] = set()
            for url in all_links[:MAX_ENTRIES]:
                if url in seen:
                    continue
                seen.add(url)
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
