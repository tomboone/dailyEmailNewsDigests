from unittest.mock import MagicMock, patch

from src.dailyemailnewsdigests.email_builder import build_html_email, send_smtp_email


def test_build_html_email_contains_subject() -> None:
    sections = [
        {
            "title": "F1",
            "items": [
                {
                    "source": "Crash > F1",
                    "title": "Test Article",
                    "link": "https://example.com",
                    "description": "A test description",
                }
            ],
        }
    ]
    html = build_html_email("News Digest", "March 17, 2026", sections)
    assert "News Digest" in html


def test_build_html_email_contains_section_title() -> None:
    sections = [
        {
            "title": "MotoGP",
            "items": [
                {
                    "source": "Motorsport > MotoGP",
                    "title": "Test",
                    "link": "https://example.com",
                    "description": "Desc",
                }
            ],
        }
    ]
    html = build_html_email("News Digest", "March 17, 2026", sections)
    assert "MotoGP" in html


def test_build_html_email_contains_article_source_and_title() -> None:
    sections = [
        {
            "title": "F1",
            "items": [
                {
                    "source": "The Race > F1",
                    "title": "Big Race News",
                    "link": "https://example.com/article",
                    "description": "Article description here",
                }
            ],
        }
    ]
    html = build_html_email("News Digest", "March 17, 2026", sections)
    assert "The Race > F1" in html
    assert "Big Race News" in html
    assert "https://example.com/article" in html
    assert "Article description here" in html


def test_build_html_email_contains_footer() -> None:
    sections = [
        {
            "title": "F1",
            "items": [
                {
                    "source": "Test",
                    "title": "Test",
                    "link": "#",
                    "description": "",
                }
            ],
        }
    ]
    html = build_html_email("My Digest", "March 17, 2026", sections)
    assert "My Digest" in html
    assert "subscribed" in html


@patch("src.dailyemailnewsdigests.email_builder.smtplib.SMTP")
def test_send_smtp_email_sends_message(mock_smtp_class: MagicMock) -> None:
    mock_server = MagicMock()
    mock_smtp_class.return_value.__enter__ = MagicMock(return_value=mock_server)
    mock_smtp_class.return_value.__exit__ = MagicMock(return_value=False)

    send_smtp_email(
        subject="Test",
        text_body="text",
        html_body="<html>html</html>",
        sender="sender@test.com",
        recipient="recipient@test.com",
    )

    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once()
    mock_server.sendmail.assert_called_once()
