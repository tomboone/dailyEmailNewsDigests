from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

import pytest
from azure.core.exceptions import ResourceExistsError

from src.dailyemailnewsdigests.storage import (
    RssItemEntity,
    delete_old_items,
    insert_new_items,
    mark_items_sent,
    query_unsent_items,
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


def test_insert_new_items_creates_new_entities(mock_table_client: MagicMock) -> None:
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
            "sent": False,
        }
    ]
    count = insert_new_items(mock_table_client, items)
    assert count == 1
    mock_table_client.create_entity.assert_called_once()


def test_insert_new_items_skips_existing(mock_table_client: MagicMock) -> None:
    mock_table_client.create_entity.side_effect = ResourceExistsError("exists")
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
            "sent": False,
        }
    ]
    count = insert_new_items(mock_table_client, items)
    assert count == 0


def test_query_unsent_items_filters_by_category(mock_table_client: MagicMock) -> None:
    entity = _make_entity(category="F1", row_key="a")
    mock_table_client.query_entities.return_value = [entity]

    results = query_unsent_items(mock_table_client, "F1")
    assert len(results) == 1
    assert results[0]["PartitionKey"] == "F1"
    call_args = mock_table_client.query_entities.call_args[0][0]
    assert "sent eq false" in call_args


def test_mark_items_sent_updates_entities(mock_table_client: MagicMock) -> None:
    items: list[dict[str, str]] = [
        _make_entity(row_key="a"),
        _make_entity(row_key="b"),
    ]
    mark_items_sent(mock_table_client, items)
    assert mock_table_client.update_entity.call_count == 2
    for item in items:
        assert item["sent"] is True


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
