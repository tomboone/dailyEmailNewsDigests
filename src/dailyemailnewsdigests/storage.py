"""Azure Table Storage operations for RSS items."""

import hashlib
import logging
from datetime import UTC, datetime, timedelta
from typing import Any, TypedDict

from azure.core.exceptions import ResourceExistsError
from azure.data.tables import TableClient, TableServiceClient

import src.dailyemailnewsdigests.config as config

TABLE_NAME = "RssItems"


class RssItemEntity(TypedDict):
    PartitionKey: str
    RowKey: str
    source: str
    title: str
    link: str
    description: str
    published: str
    fetched_at: str
    sent: bool


def make_row_key(link: str) -> str:
    """Generate a deterministic RowKey from an article link."""
    return hashlib.sha256(link.encode()).hexdigest()


def get_table_client() -> TableClient:
    """Create and return a TableClient for the RssItems table."""
    service = TableServiceClient.from_connection_string(config.AZURE_STORAGE_CONNECTION_STRING)
    service.create_table_if_not_exists(TABLE_NAME)
    return service.get_table_client(TABLE_NAME)


def insert_new_items(client: TableClient, items: list[RssItemEntity]) -> int:
    """Insert items that don't already exist. Returns count of new items inserted."""
    inserted = 0
    for item in items:
        try:
            client.create_entity(item)
            inserted += 1
        except ResourceExistsError:
            pass
    return inserted


def query_unsent_items(client: TableClient, category: str) -> list[dict[str, Any]]:
    """Query items for a category that have not yet been included in a digest."""
    query_filter = f"PartitionKey eq '{category}' and sent eq false"
    return list(client.query_entities(query_filter))


def mark_items_sent(client: TableClient, items: list[dict[str, Any]]) -> None:
    """Mark a list of items as sent."""
    for item in items:
        item["sent"] = True
        client.update_entity(item)


def delete_old_items(client: TableClient, max_age_days: int = 365) -> None:
    """Delete items older than max_age_days from the table."""
    cutoff = datetime.now(UTC) - timedelta(days=max_age_days)
    all_entities = client.query_entities("")
    deleted = 0
    for entity in all_entities:
        fetched_at = datetime.fromisoformat(entity["fetched_at"])
        if fetched_at < cutoff:
            client.delete_entity(entity["PartitionKey"], entity["RowKey"])
            deleted += 1
    if deleted:
        logging.info(f"Cleaned up {deleted} old items from {TABLE_NAME}.")
