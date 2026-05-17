import responses as resp_lib
from scraper.sources.newsrooms import get_articles, NEWSROOMS

NEWSROOM_HTML = """
<html><body>
  <a href="/en/media/press-releases/cdr-deal-2024">CDR Deal 2024</a>
</body></html>"""

PRESS_HTML = "<html><body><p>Press release about CDR deal</p></body></html>"


@resp_lib.activate
def test_get_articles_returns_empty_when_all_fail():
    for _, url in NEWSROOMS:
        resp_lib.add(resp_lib.GET, url, status=500)

    articles = get_articles()

    assert articles == []


@resp_lib.activate
def test_get_articles_fetches_press_releases():
    company_name, newsroom_url = NEWSROOMS[0]
    domain = "https://" + newsroom_url.split("/")[2]

    resp_lib.add(resp_lib.GET, newsroom_url, body=NEWSROOM_HTML)
    resp_lib.add(resp_lib.GET, f"{domain}/en/media/press-releases/cdr-deal-2024", body=PRESS_HTML)
    for _, url in NEWSROOMS[1:]:
        resp_lib.add(resp_lib.GET, url, status=500)

    articles = get_articles()

    assert len(articles) >= 1
    assert any("Press release" in a.text for a in articles)
