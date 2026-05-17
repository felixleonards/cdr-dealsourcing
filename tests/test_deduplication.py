import json
from scraper.deduplication import load_seen_urls, save_seen_urls, is_new


def test_load_seen_urls_empty_file(tmp_path, monkeypatch):
    monkeypatch.setattr("scraper.deduplication.SEEN_URLS_PATH", tmp_path / "seen_urls.json")
    (tmp_path / "seen_urls.json").write_text("[]")
    assert load_seen_urls() == set()


def test_load_seen_urls_with_entries(tmp_path, monkeypatch):
    monkeypatch.setattr("scraper.deduplication.SEEN_URLS_PATH", tmp_path / "seen_urls.json")
    (tmp_path / "seen_urls.json").write_text('["https://example.com/a", "https://example.com/b"]')
    assert load_seen_urls() == {"https://example.com/a", "https://example.com/b"}


def test_load_seen_urls_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr("scraper.deduplication.SEEN_URLS_PATH", tmp_path / "seen_urls.json")
    assert load_seen_urls() == set()


def test_save_seen_urls(tmp_path, monkeypatch):
    path = tmp_path / "seen_urls.json"
    monkeypatch.setattr("scraper.deduplication.SEEN_URLS_PATH", path)
    save_seen_urls({"https://example.com/a", "https://example.com/b"})
    data = json.loads(path.read_text())
    assert set(data) == {"https://example.com/a", "https://example.com/b"}


def test_is_new_returns_true_for_unseen():
    assert is_new("https://new.com", set()) is True


def test_is_new_returns_false_for_seen():
    assert is_new("https://seen.com", {"https://seen.com"}) is False
