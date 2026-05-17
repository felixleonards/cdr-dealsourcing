import os
import traceback
from scraper.sources import carbon_herald, gcca, press_wires, puro_earth, carbonfuture, newsrooms, cdr_fyi
from scraper.extractor import extract_deal
from scraper.sheets_writer import write_deal
from scraper.deduplication import load_seen_urls, save_seen_urls, is_new

ALL_SOURCES = [
    carbon_herald.get_archive_articles,  # historical archive first
    carbon_herald.get_articles,           # then recent RSS
    gcca.get_articles,
    press_wires.get_articles,
    puro_earth.get_articles,
    carbonfuture.get_articles,
    newsrooms.get_articles,
    cdr_fyi.get_articles,
]


def run(nvidia_key: str, credentials_json: str, sheet_id: str) -> None:
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
                write_deal(deal, credentials_json, sheet_id)
                deals_written += 1
                print(f"[OK] {article.url}")
            except Exception as e:
                print(f"[ERROR] Writing deal from {article.url}: {e!r}")
                traceback.print_exc()

    seen.update(new_urls)
    save_seen_urls(seen)
    print(f"Done. {deals_written} new deals written.")


if __name__ == "__main__":
    run(
        nvidia_key=os.environ["NVIDIA_API_KEY"],
        credentials_json=os.environ["GOOGLE_CREDENTIALS"],
        sheet_id=os.environ["GOOGLE_SHEET_ID"],
    )
