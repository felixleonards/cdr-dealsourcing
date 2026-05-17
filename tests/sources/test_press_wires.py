import responses as resp_lib
from scraper.sources.press_wires import get_articles, BUSINESS_WIRE_URL, SEARCH_QUERIES

SEARCH_HTML = """
<html><body>
  <a class="bwTitleLink" href="/news/home/12345">CDR Deal for Cement</a>
</body></html>"""

ARTICLE_HTML = "<html><body><p>Heidelberg Materials signs CDR deal</p></body></html>"
EMPTY_HTML = "<html><body></body></html>"


@resp_lib.activate
def test_get_articles_finds_links():
    resp_lib.add(resp_lib.GET, BUSINESS_WIRE_URL.format(query=SEARCH_QUERIES[0]), body=SEARCH_HTML)
    for q in SEARCH_QUERIES[1:]:
        resp_lib.add(resp_lib.GET, BUSINESS_WIRE_URL.format(query=q), body=EMPTY_HTML)
    resp_lib.add(resp_lib.GET, "https://www.businesswire.com/news/home/12345", body=ARTICLE_HTML)

    articles = get_articles()

    assert len(articles) == 1
    assert "Heidelberg Materials" in articles[0].text


@resp_lib.activate
def test_get_articles_deduplicates_across_queries():
    for q in SEARCH_QUERIES:
        resp_lib.add(resp_lib.GET, BUSINESS_WIRE_URL.format(query=q), body=SEARCH_HTML)
    resp_lib.add(resp_lib.GET, "https://www.businesswire.com/news/home/12345", body=ARTICLE_HTML)

    articles = get_articles()

    assert len(articles) == 1
