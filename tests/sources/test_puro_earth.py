from scraper.sources.puro_earth import get_articles, PROJECT_LIST_URL


def test_get_articles_returns_articles(mocker):
    mock_page = mocker.MagicMock()
    mock_page.eval_on_selector_all.return_value = [
        "https://puro.earth/projects/biochar-1",
        "https://puro.earth/projects/beccs-2",
    ]
    mock_page.inner_text.return_value = "Project description with CDR info"

    mock_browser = mocker.MagicMock()
    mock_browser.new_page.return_value = mock_page

    mock_pw = mocker.MagicMock()
    mock_pw.__enter__ = mocker.MagicMock(return_value=mock_pw)
    mock_pw.__exit__ = mocker.MagicMock(return_value=False)
    mock_pw.chromium.launch.return_value = mock_browser

    mocker.patch("scraper.sources.puro_earth.sync_playwright", return_value=mock_pw)

    articles = get_articles()

    assert len(articles) == 2
    assert articles[0].url == "https://puro.earth/projects/biochar-1"
    assert articles[0].text == "Project description with CDR info"


def test_get_articles_skips_failed_pages(mocker):
    mock_page = mocker.MagicMock()
    mock_page.eval_on_selector_all.return_value = ["https://puro.earth/projects/project-1"]
    mock_page.inner_text.side_effect = Exception("Page load failed")

    mock_browser = mocker.MagicMock()
    mock_browser.new_page.return_value = mock_page

    mock_pw = mocker.MagicMock()
    mock_pw.__enter__ = mocker.MagicMock(return_value=mock_pw)
    mock_pw.__exit__ = mocker.MagicMock(return_value=False)
    mock_pw.chromium.launch.return_value = mock_browser

    mocker.patch("scraper.sources.puro_earth.sync_playwright", return_value=mock_pw)

    articles = get_articles()

    assert articles == []
