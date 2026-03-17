from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest

from src.dailyemailnewsdigests.storage import (
    RssItemEntity,
    delete_old_items,
    query_recent_items,
    upsert_items,
)


@pytest.fixture
def mock_table_client() -> MagicMock:
    return MagicMock()


def _make_entity(
    category: str = "F1",
    row_key: str = "abc123",
    fetched_hours_ago: int = 0,
) -> dict[str, str]:
    fetched = datetime.now(timezone.utc) - timedelta(hours=fetched_hours_ago)
    return {
        "PartitionKey": category,
        "RowKey": row_key,
        "source": "Test Source",
        "title": "Test Title",
        "link": "https://example.com/article",
        "description": "Test description",
        "published": "2026-03-17T10:00:00+00:00",
        "fetched_at": fetched.isoformat(),
    }


def test_upsert_items_calls_upsert_for_each_item(mock_table_client: MagicMock) -> None:
    items: list[RssItemEntity] = [
        {
            "PartitionKey": "F1",
            "RowKey": "abc",
            "source": "Test",
            "title": "Title",
            "link": "https://example.com",
            "description": "Desc",
            "published": "2026-03-17T10:00:00+00:00",
            "fetched_at": datetime.now(timezone.utc).isoformat(),
        }
    ]
    upsert_items(mock_table_client, items)
    mock_table_client.upsert_entity.assert_called_once()


def test_query_recent_items_filters_by_category(mock_table_client: MagicMock) -> None:
    recent = _make_entity(category="F1", row_key="a", fetched_hours_ago=1)
    mock_table_client.query_entities.return_value = [recent]

    results = query_recent_items(mock_table_client, "F1", hours=24)
    assert len(results) == 1
    assert results[0]["PartitionKey"] == "F1"
    mock_table_client.query_entities.assert_called_once()


def test_delete_old_items_deletes_expired(mock_table_client: MagicMock) -> None:
    old = _make_entity(fetched_hours_ago=200)
    mock_table_client.query_entities.return_value = [old]

    delete_old_items(mock_table_client, max_age_days=7)
    mock_table_client.delete_entity.assert_called_once()


def test_delete_old_items_keeps_recent(mock_table_client: MagicMock) -> None:
    recent = _make_entity(fetched_hours_ago=1)
    mock_table_client.query_entities.return_value = [recent]

    delete_old_items(mock_table_client, max_age_days=7)
    mock_table_client.delete_entity.assert_not_called()
