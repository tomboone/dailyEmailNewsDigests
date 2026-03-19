from typing import Any
from unittest.mock import MagicMock, patch

import pytest


@pytest.fixture
def sample_feed_entry() -> dict[str, Any]:
    """A feedparser entry simulating one RSS item."""
    return {
        "title": "Test Article Title",
        "link": "https://example.com/article-1",
        "summary": "Some description text...Keep reading",
        "published_parsed": (2026, 3, 17, 10, 0, 0, 0, 76, 0),
    }


@pytest.fixture
def sample_feeds_config() -> dict[str, Any]:
    return {
        "recipient": "test@example.com",
        "categories": [
            {
                "title": "F1",
                "feeds": [
                    {
                        "source": "Test Source > F1",
                        "url": "https://example.com/rss/f1",
                    }
                ],
            }
        ],
    }


@patch("src.dailyemailnewsdigests.blueprints.bp_rss_fetcher.delete_old_items")
@patch("src.dailyemailnewsdigests.blueprints.bp_rss_fetcher.insert_new_items")
@patch("src.dailyemailnewsdigests.blueprints.bp_rss_fetcher.get_table_client")
@patch("src.dailyemailnewsdigests.blueprints.bp_rss_fetcher.feedparser.parse")
@patch("src.dailyemailnewsdigests.blueprints.bp_rss_fetcher.load_feeds")
def test_fetch_rss_feeds_stores_items(
    mock_load_feeds: MagicMock,
    mock_parse: MagicMock,
    mock_get_client: MagicMock,
    mock_insert: MagicMock,
    mock_delete: MagicMock,
    sample_feeds_config: dict[str, Any],
    sample_feed_entry: dict[str, Any],
) -> None:
    mock_load_feeds.return_value = sample_feeds_config
    mock_parse.return_value = MagicMock(
        entries=[sample_feed_entry],
        bozo=False,
    )
    mock_insert.return_value = 1
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    from src.dailyemailnewsdigests.blueprints.bp_rss_fetcher import fetch_rss_feeds

    fetch_rss_feeds(MagicMock())

    mock_insert.assert_called_once()
    items = mock_insert.call_args[0][1]
    assert len(items) == 1
    assert items[0]["PartitionKey"] == "F1"
    assert items[0]["source"] == "Test Source > F1"
    assert items[0]["title"] == "Test Article Title"
    assert "Keep reading" not in items[0]["description"]


@patch("src.dailyemailnewsdigests.blueprints.bp_rss_fetcher.delete_old_items")
@patch("src.dailyemailnewsdigests.blueprints.bp_rss_fetcher.insert_new_items")
@patch("src.dailyemailnewsdigests.blueprints.bp_rss_fetcher.get_table_client")
@patch("src.dailyemailnewsdigests.blueprints.bp_rss_fetcher.feedparser.parse")
@patch("src.dailyemailnewsdigests.blueprints.bp_rss_fetcher.load_feeds")
def test_fetch_rss_feeds_continues_on_feed_error(
    mock_load_feeds: MagicMock,
    mock_parse: MagicMock,
    mock_get_client: MagicMock,
    mock_insert: MagicMock,
    mock_delete: MagicMock,
    sample_feed_entry: dict[str, Any],
) -> None:
    mock_load_feeds.return_value = {
        "recipient": "test@example.com",
        "categories": [
            {
                "title": "F1",
                "feeds": [
                    {"source": "Bad Feed", "url": "https://example.com/bad"},
                    {"source": "Good Feed", "url": "https://example.com/good"},
                ],
            }
        ],
    }
    mock_parse.side_effect = [
        MagicMock(bozo=True, bozo_exception=Exception("parse error"), entries=[]),
        MagicMock(bozo=False, entries=[sample_feed_entry]),
    ]
    mock_insert.return_value = 1
    mock_get_client.return_value = MagicMock()

    from src.dailyemailnewsdigests.blueprints.bp_rss_fetcher import fetch_rss_feeds

    fetch_rss_feeds(MagicMock())

    mock_insert.assert_called_once()
    items = mock_insert.call_args[0][1]
    assert len(items) == 1


@patch("src.dailyemailnewsdigests.blueprints.bp_rss_fetcher.delete_old_items")
@patch("src.dailyemailnewsdigests.blueprints.bp_rss_fetcher.insert_new_items")
@patch("src.dailyemailnewsdigests.blueprints.bp_rss_fetcher.get_table_client")
@patch("src.dailyemailnewsdigests.blueprints.bp_rss_fetcher.feedparser.parse")
@patch("src.dailyemailnewsdigests.blueprints.bp_rss_fetcher.load_feeds")
def test_fetch_rss_feeds_calls_cleanup(
    mock_load_feeds: MagicMock,
    mock_parse: MagicMock,
    mock_get_client: MagicMock,
    mock_insert: MagicMock,
    mock_delete: MagicMock,
    sample_feeds_config: dict[str, Any],
) -> None:
    mock_load_feeds.return_value = sample_feeds_config
    mock_parse.return_value = MagicMock(entries=[], bozo=False)
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client

    from src.dailyemailnewsdigests.blueprints.bp_rss_fetcher import fetch_rss_feeds

    fetch_rss_feeds(MagicMock())

    mock_delete.assert_called_once_with(mock_client)
