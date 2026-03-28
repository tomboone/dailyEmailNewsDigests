from datetime import UTC, datetime, timedelta
from unittest.mock import MagicMock, patch


@patch("src.dailyemailnewsdigests.blueprints.bp_digests.mark_items_sent")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.send_smtp_email")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.build_html_email")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.build_plain_text_email")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.query_unsent_items")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.get_table_client")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.load_feeds")
def test_digest_email_sends_email(
    mock_load_feeds: MagicMock,
    mock_get_client: MagicMock,
    mock_query: MagicMock,
    mock_plain: MagicMock,
    mock_html: MagicMock,
    mock_send: MagicMock,
    mock_mark_sent: MagicMock,
) -> None:
    mock_load_feeds.return_value = {
        "recipient": "test@example.com",
        "categories": [
            {
                "title": "F1",
                "feeds": [{"source": "Crash > F1", "url": "https://example.com/rss"}],
            }
        ],
    }
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    mock_query.return_value = [
        {
            "PartitionKey": "F1",
            "RowKey": "abc123",
            "source": "Crash > F1",
            "title": "Test Article",
            "link": "https://example.com/article",
            "description": "A test description",
            "published": datetime.now(UTC).isoformat(),
            "fetched_at": datetime.now(UTC).isoformat(),
            "sent": False,
        }
    ]
    mock_html.return_value = "<html>test</html>"
    mock_plain.return_value = "plain text"

    from src.dailyemailnewsdigests.blueprints.bp_digests import digest_email

    digest_email(MagicMock())

    mock_send.assert_called_once()
    call_kwargs = mock_send.call_args
    assert call_kwargs[1]["recipient"] == "test@example.com"
    mock_mark_sent.assert_called_once_with(mock_client, mock_query.return_value)


@patch("src.dailyemailnewsdigests.blueprints.bp_digests.send_smtp_email")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.query_unsent_items")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.get_table_client")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.load_feeds")
def test_digest_email_skips_empty_categories(
    mock_load_feeds: MagicMock,
    mock_get_client: MagicMock,
    mock_query: MagicMock,
    mock_send: MagicMock,
) -> None:
    mock_load_feeds.return_value = {
        "recipient": "test@example.com",
        "categories": [
            {
                "title": "F1",
                "feeds": [{"source": "Test", "url": "https://example.com/rss"}],
            }
        ],
    }
    mock_get_client.return_value = MagicMock()
    mock_query.return_value = []

    from src.dailyemailnewsdigests.blueprints.bp_digests import digest_email

    digest_email(MagicMock())

    mock_send.assert_not_called()


@patch("src.dailyemailnewsdigests.blueprints.bp_digests.mark_items_sent")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.send_smtp_email")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.build_html_email")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.build_plain_text_email")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.query_unsent_items")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.get_table_client")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.load_feeds")
def test_digest_email_does_not_mark_sent_on_failure(
    mock_load_feeds: MagicMock,
    mock_get_client: MagicMock,
    mock_query: MagicMock,
    mock_plain: MagicMock,
    mock_html: MagicMock,
    mock_send: MagicMock,
    mock_mark_sent: MagicMock,
) -> None:
    mock_load_feeds.return_value = {
        "recipient": "test@example.com",
        "categories": [
            {
                "title": "F1",
                "feeds": [{"source": "Test", "url": "https://example.com/rss"}],
            }
        ],
    }
    mock_get_client.return_value = MagicMock()
    mock_query.return_value = [
        {
            "PartitionKey": "F1",
            "RowKey": "abc123",
            "source": "Test",
            "title": "Article",
            "link": "https://example.com/article",
            "description": "Desc",
            "published": datetime.now(UTC).isoformat(),
            "fetched_at": datetime.now(UTC).isoformat(),
            "sent": False,
        }
    ]
    mock_html.return_value = "<html>test</html>"
    mock_plain.return_value = "plain text"
    mock_send.side_effect = Exception("SMTP error")

    from src.dailyemailnewsdigests.blueprints.bp_digests import digest_email

    digest_email(MagicMock())

    mock_mark_sent.assert_not_called()


@patch("src.dailyemailnewsdigests.blueprints.bp_digests.mark_items_sent")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.send_smtp_email")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.build_html_email")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.build_plain_text_email")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.query_unsent_items")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.get_table_client")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.load_feeds")
def test_digest_email_marks_stale_items_as_sent(
    mock_load_feeds: MagicMock,
    mock_get_client: MagicMock,
    mock_query: MagicMock,
    mock_plain: MagicMock,
    mock_html: MagicMock,
    mock_send: MagicMock,
    mock_mark_sent: MagicMock,
) -> None:
    mock_load_feeds.return_value = {
        "recipient": "test@example.com",
        "categories": [
            {
                "title": "F1",
                "feeds": [{"source": "Test", "url": "https://example.com/rss"}],
            }
        ],
    }
    mock_client = MagicMock()
    mock_get_client.return_value = mock_client
    stale_item = {
        "PartitionKey": "F1",
        "RowKey": "stale123",
        "source": "Test",
        "title": "Old Article",
        "link": "https://example.com/old",
        "description": "Stale desc",
        "published": (datetime.now(UTC) - timedelta(hours=72)).isoformat(),
        "fetched_at": (datetime.now(UTC) - timedelta(hours=72)).isoformat(),
        "sent": False,
    }
    recent_item = {
        "PartitionKey": "F1",
        "RowKey": "recent123",
        "source": "Test",
        "title": "New Article",
        "link": "https://example.com/new",
        "description": "Recent desc",
        "published": datetime.now(UTC).isoformat(),
        "fetched_at": datetime.now(UTC).isoformat(),
        "sent": False,
    }
    mock_query.return_value = [stale_item, recent_item]
    mock_html.return_value = "<html>test</html>"
    mock_plain.return_value = "plain text"

    from src.dailyemailnewsdigests.blueprints.bp_digests import digest_email

    digest_email(MagicMock())

    mock_send.assert_called_once()
    assert mock_mark_sent.call_count == 2
    mock_mark_sent.assert_any_call(mock_client, [stale_item])
    mock_mark_sent.assert_any_call(mock_client, [recent_item])
