import responses as resp_lib
from unittest.mock import patch
import feedparser
from scraper.sources.rss import fetch_rss_articles
from scraper.sources.base import Article

RSS_FIXTURE = """<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <title>Test Feed</title>
    <item>
      <title>CDR Deal Announced</title>
      <link>https://example.com/article-1</link>
    </item>
    <item>
      <title>Another Article</title>
      <link>https://example.com/article-2</link>
    </item>
  </channel>
</rss>"""

ARTICLE_HTML = "<html><body><p>Deal content here</p></body></html>"

# Pre-parse the feed outside of any patch context
PARSED_FEED = feedparser.parse(RSS_FIXTURE)


@resp_lib.activate
def test_fetch_rss_articles_returns_articles():
    # Mock feedparser.parse to return the parsed RSS fixture
    with patch('scraper.sources.rss.feedparser.parse') as mock_parse:
        mock_parse.return_value = PARSED_FEED

        resp_lib.add(resp_lib.GET, "https://example.com/article-1", body=ARTICLE_HTML)
        resp_lib.add(resp_lib.GET, "https://example.com/article-2", body=ARTICLE_HTML)

        articles = fetch_rss_articles("https://example.com/feed/")

        assert len(articles) == 2
        assert all(isinstance(a, Article) for a in articles)
        assert articles[0].url == "https://example.com/article-1"
        assert "Deal content here" in articles[0].text


@resp_lib.activate
def test_fetch_rss_articles_skips_failed_requests():
    # Mock feedparser.parse to return the parsed RSS fixture
    with patch('scraper.sources.rss.feedparser.parse') as mock_parse:
        mock_parse.return_value = PARSED_FEED

        resp_lib.add(resp_lib.GET, "https://example.com/article-1", status=404)
        resp_lib.add(resp_lib.GET, "https://example.com/article-2", body=ARTICLE_HTML)

        articles = fetch_rss_articles("https://example.com/feed/")

        assert len(articles) == 1
        assert articles[0].url == "https://example.com/article-2"
