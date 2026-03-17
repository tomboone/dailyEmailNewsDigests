from unittest.mock import MagicMock, patch


@patch("src.dailyemailnewsdigests.blueprints.bp_digests.send_smtp_email")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.build_html_email")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.build_plain_text_email")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.query_recent_items")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.get_table_client")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.load_feeds")
def test_digest_email_sends_email(
    mock_load_feeds: MagicMock,
    mock_get_client: MagicMock,
    mock_query: MagicMock,
    mock_plain: MagicMock,
    mock_html: MagicMock,
    mock_send: MagicMock,
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
    mock_get_client.return_value = MagicMock()
    mock_query.return_value = [
        {
            "PartitionKey": "F1",
            "RowKey": "abc123",
            "source": "Crash > F1",
            "title": "Test Article",
            "link": "https://example.com/article",
            "description": "A test description",
            "published": "2026-03-17T10:00:00+00:00",
            "fetched_at": "2026-03-17T09:00:00+00:00",
        }
    ]
    mock_html.return_value = "<html>test</html>"
    mock_plain.return_value = "plain text"

    from src.dailyemailnewsdigests.blueprints.bp_digests import digest_email

    digest_email(MagicMock())

    mock_send.assert_called_once()
    call_kwargs = mock_send.call_args
    assert call_kwargs[1]["recipient"] == "test@example.com"


@patch("src.dailyemailnewsdigests.blueprints.bp_digests.send_smtp_email")
@patch("src.dailyemailnewsdigests.blueprints.bp_digests.query_recent_items")
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
