import responses as resp_lib
from unittest.mock import patch
import feedparser
from scraper.sources.gcca import get_articles, FEED_URL

RSS_FIXTURE = """<?xml version="1.0"?>
<rss version="2.0">
  <channel>
    <item><title>Test</title><link>https://gccassociation.org/news/article-1</link></item>
  </channel>
</rss>"""

# Pre-parse the feed outside of any patch context
PARSED_FEED = feedparser.parse(RSS_FIXTURE)


@resp_lib.activate
def test_get_articles_uses_correct_feed():
    with patch('scraper.sources.rss.feedparser.parse') as mock_parse:
        mock_parse.return_value = PARSED_FEED

        resp_lib.add(resp_lib.GET, "https://gccassociation.org/news/article-1", body="<html><body>text</body></html>")

        articles = get_articles()

        assert len(articles) == 1


@resp_lib.activate
def test_get_articles_returns_empty_on_feed_failure():
    with patch('scraper.sources.rss.feedparser.parse') as mock_parse:
        mock_parse.side_effect = Exception("Feed fetch failed")

        articles = get_articles()

        assert articles == []
