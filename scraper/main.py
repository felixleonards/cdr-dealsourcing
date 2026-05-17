import os
from scraper.sources import carbon_herald, gcca, press_wires, puro_earth, carbonfuture, newsrooms
from scraper.extractor import extract_deal
from scraper.notion_writer import write_deal
from scraper.deduplication import load_seen_urls, save_seen_urls, is_new

ALL_SOURCES = [
    carbon_herald.get_articles,
    gcca.get_articles,
    press_wires.get_articles,
    puro_earth.get_articles,
    carbonfuture.get_articles,
    newsrooms.get_articles,
]


def run(nvidia_key: str, notion_token: str, database_id: str) -> None:
    seen = load_seen_urls()
    new_urls: set[str] = set()
    deals_written = 0

    for get_articles in ALL_SOURCES:
        try:
            articles = get_articles()
        except Exception as e:
            print(f"[ERROR] {get_articles.__module__}: {e}")
            continue

        for article in articles:
            if not is_new(article.url, seen):
                continue
            new_urls.add(article.url)

            deal = extract_deal(article.text, nvidia_key)
            if deal is None:
                continue

            deal["quelle"] = article.url
            try:
                write_deal(deal, database_id, notion_token)
                deals_written += 1
                print(f"[OK] {article.url}")
            except Exception as e:
                print(f"[ERROR] Writing deal from {article.url}: {e}")

    seen.update(new_urls)
    save_seen_urls(seen)
    print(f"Done. {deals_written} new deals written.")


if __name__ == "__main__":
    run(
        nvidia_key=os.environ["NVIDIA_API_KEY"],
        notion_token=os.environ["NOTION_API_KEY"],
        database_id=os.environ["NOTION_DATABASE_ID"],
    )
