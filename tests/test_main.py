from scraper.main import run
from scraper.sources.base import Article


def test_run_writes_new_deals_to_notion(mocker, tmp_path):
    mocker.patch("scraper.deduplication.SEEN_URLS_PATH", tmp_path / "seen_urls.json")
    (tmp_path / "seen_urls.json").write_text("[]")

    mock_articles = [Article(url="https://example.com/deal-1", text="CDR deal article text")]
    mock_deal = {"kaeufer": "Heidelberg Materials", "verkaeufer": "CarbonCure", "zementrelevant": True}

    mocker.patch("scraper.main.ALL_SOURCES", [lambda: mock_articles])
    mocker.patch("scraper.main.extract_deal", return_value=mock_deal)
    mock_write = mocker.patch("scraper.main.write_deal")

    run(nvidia_key="test-key", notion_token="test-token", database_id="test-db")

    mock_write.assert_called_once()
    written_deal = mock_write.call_args[0][0]
    assert written_deal["quelle"] == "https://example.com/deal-1"


def test_run_skips_already_seen_urls(mocker, tmp_path):
    mocker.patch("scraper.deduplication.SEEN_URLS_PATH", tmp_path / "seen_urls.json")
    (tmp_path / "seen_urls.json").write_text('["https://example.com/deal-1"]')

    mock_articles = [Article(url="https://example.com/deal-1", text="CDR deal article text")]
    mocker.patch("scraper.main.ALL_SOURCES", [lambda: mock_articles])
    mock_extract = mocker.patch("scraper.main.extract_deal")

    run(nvidia_key="test-key", notion_token="test-token", database_id="test-db")

    mock_extract.assert_not_called()


def test_run_skips_articles_with_no_deal(mocker, tmp_path):
    mocker.patch("scraper.deduplication.SEEN_URLS_PATH", tmp_path / "seen_urls.json")
    (tmp_path / "seen_urls.json").write_text("[]")

    mock_articles = [Article(url="https://example.com/no-deal", text="Unrelated article")]
    mocker.patch("scraper.main.ALL_SOURCES", [lambda: mock_articles])
    mocker.patch("scraper.main.extract_deal", return_value=None)
    mock_write = mocker.patch("scraper.main.write_deal")

    run(nvidia_key="test-key", notion_token="test-token", database_id="test-db")

    mock_write.assert_not_called()


def test_run_continues_when_source_fails(mocker, tmp_path):
    mocker.patch("scraper.deduplication.SEEN_URLS_PATH", tmp_path / "seen_urls.json")
    (tmp_path / "seen_urls.json").write_text("[]")

    failing_source = mocker.MagicMock(side_effect=Exception("Network error"))
    good_articles = [Article(url="https://example.com/deal", text="CDR deal")]
    good_source = mocker.MagicMock(return_value=good_articles)

    mocker.patch("scraper.main.ALL_SOURCES", [failing_source, good_source])
    mocker.patch("scraper.main.extract_deal", return_value={"kaeufer": "A", "verkaeufer": "B"})
    mock_write = mocker.patch("scraper.main.write_deal")

    run(nvidia_key="test-key", notion_token="test-token", database_id="test-db")

    mock_write.assert_called_once()
