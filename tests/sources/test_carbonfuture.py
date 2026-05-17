import responses as resp_lib
from scraper.sources.carbonfuture import get_articles, REGISTRY_URL, BASE_URL

INDEX_HTML = """
<html><body>
  <a href="/registry/project-biochar-1">Biochar Project</a>
  <a href="/registry/project-beccs-2">BECCS Project</a>
</body></html>"""

PROJECT_HTML = "<html><body><p>CDR project details</p></body></html>"


@resp_lib.activate
def test_get_articles_fetches_project_pages():
    resp_lib.add(resp_lib.GET, REGISTRY_URL, body=INDEX_HTML)
    resp_lib.add(resp_lib.GET, f"{BASE_URL}/registry/project-biochar-1", body=PROJECT_HTML)
    resp_lib.add(resp_lib.GET, f"{BASE_URL}/registry/project-beccs-2", body=PROJECT_HTML)

    articles = get_articles()

    assert len(articles) == 2


@resp_lib.activate
def test_get_articles_returns_empty_on_failure():
    resp_lib.add(resp_lib.GET, REGISTRY_URL, status=500)

    articles = get_articles()

    assert articles == []
