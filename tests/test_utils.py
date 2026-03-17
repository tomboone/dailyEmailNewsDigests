from typing import Any

from src.dailyemailnewsdigests.utils import clean_description, load_feeds


def test_clean_description_removes_title_prefix() -> None:
    text = "Article Title Some actual description text"
    result = clean_description(text, "Article Title")
    assert result == ""


def test_clean_description_removes_keep_reading() -> None:
    text = "Some description text...Keep reading"
    result = clean_description(text, "Unrelated Title")
    assert result == "Some description text"


def test_clean_description_removes_ellipsis_bracket() -> None:
    text = "Some description text [\u2026]"
    result = clean_description(text, "Unrelated Title")
    assert result == "Some description text"


def test_clean_description_removes_parenthetical_ellipsis() -> None:
    text = "Some description text (...)"
    result = clean_description(text, "Unrelated Title")
    assert result == "Some description text"


def test_clean_description_strips_whitespace() -> None:
    text = "  Some description text  "
    result = clean_description(text, "Unrelated Title")
    assert result == "Some description text"


def test_load_feeds_returns_valid_structure() -> None:
    feeds: dict[str, Any] = load_feeds()
    assert "recipient" in feeds
    assert "categories" in feeds
    assert isinstance(feeds["categories"], list)
    assert len(feeds["categories"]) > 0
    for category in feeds["categories"]:
        assert "title" in category
        assert "feeds" in category
        for feed in category["feeds"]:
            assert "source" in feed
            assert "url" in feed
