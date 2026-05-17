import json
from pathlib import Path

SEEN_URLS_PATH = Path(__file__).parent.parent / "seen_urls.json"


def load_seen_urls() -> set[str]:
    if not SEEN_URLS_PATH.exists():
        return set()
    with open(SEEN_URLS_PATH, encoding="utf-8-sig") as f:
        return set(json.load(f))


def save_seen_urls(urls: set[str]) -> None:
    with open(SEEN_URLS_PATH, "w") as f:
        json.dump(sorted(urls), f, indent=2)


def is_new(url: str, seen: set[str]) -> bool:
    return url not in seen
