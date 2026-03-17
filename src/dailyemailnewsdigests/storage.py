"""Azure Table Storage operations for RSS items."""

import hashlib
import logging
from datetime import datetime, timedelta, timezone
from typing import TypedDict

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


def make_row_key(link: str) -> str:
    """Generate a deterministic RowKey from an article link."""
    return hashlib.sha256(link.encode()).hexdigest()


def get_table_client() -> TableClient:
    """Create and return a TableClient for the RssItems table."""
    service = TableServiceClient.from_connection_string(config.AZURE_STORAGE_CONNECTION_STRING)
    service.create_table_if_not_exists(TABLE_NAME)
    return service.get_table_client(TABLE_NAME)


def upsert_items(client: TableClient, items: list[RssItemEntity]) -> None:
    """Upsert a list of RSS item entities into the table."""
    for item in items:
        client.upsert_entity(item)


def query_recent_items(client: TableClient, category: str, hours: int = 24) -> list[dict[str, str]]:
    """Query items for a category fetched within the given time window."""
    cutoff = (datetime.now(timezone.utc) - timedelta(hours=hours)).isoformat()
    query_filter = f"PartitionKey eq '{category}' and fetched_at ge '{cutoff}'"
    return list(client.query_entities(query_filter))


def delete_old_items(client: TableClient, max_age_days: int = 7) -> None:
    """Delete items older than max_age_days from the table."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
    all_entities = client.query_entities("")
    deleted = 0
    for entity in all_entities:
        fetched_at = datetime.fromisoformat(entity["fetched_at"])
        if fetched_at < cutoff:
            client.delete_entity(entity["PartitionKey"], entity["RowKey"])
            deleted += 1
    if deleted:
        logging.info(f"Cleaned up {deleted} old items from {TABLE_NAME}.")
