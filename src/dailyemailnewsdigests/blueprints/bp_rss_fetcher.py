"""Blueprint for fetching RSS feeds and storing items in Azure Table Storage."""

import logging
from calendar import timegm
from datetime import datetime, timezone
from time import struct_time
from typing import cast

import azure.functions as func
import feedparser

import src.dailyemailnewsdigests.config as config
from src.dailyemailnewsdigests.storage import (
    RssItemEntity,
    delete_old_items,
    get_table_client,
    make_row_key,
    upsert_items,
)
from src.dailyemailnewsdigests.utils import clean_description, load_feeds

bp: func.Blueprint = func.Blueprint()

FEED_TIMEOUT_SECONDS = 30


# noinspection PyUnusedLocal
@bp.timer_trigger(
    schedule=config.RSS_FETCH_NCRON,
    arg_name="fetch_timer",
    run_on_startup=False,
)
def fetch_rss_feeds(fetch_timer: func.TimerRequest) -> None:
    """Timer trigger to fetch RSS feeds and store items in Table Storage."""
    feeds_config = load_feeds()
    client = get_table_client()
    now = datetime.now(timezone.utc)

    for category in feeds_config["categories"]:
        category_title: str = category["title"]
        items: list[RssItemEntity] = []

        for feed_def in category["feeds"]:
            source: str = feed_def["source"]
            url: str = feed_def["url"]

            try:
                parsed = feedparser.parse(url)
                if parsed.bozo and not parsed.entries:
                    logging.warning(
                        f"Failed to parse feed '{source}' ({url}): {parsed.bozo_exception}"
                    )
                    continue

                for entry in parsed.entries:
                    published_str = now.isoformat()
                    if hasattr(entry, "published_parsed") and entry.published_parsed:
                        published_dt = datetime.fromtimestamp(
                            timegm(cast(struct_time, entry.published_parsed)),
                            tz=timezone.utc,
                        )
                        published_str = published_dt.isoformat()

                    raw_desc = cast(str, entry.get("summary", ""))
                    entry_title = cast(str, entry.get("title", ""))
                    entry_link = cast(str, entry.get("link", ""))

                    items.append(
                        RssItemEntity(
                            PartitionKey=category_title,
                            RowKey=make_row_key(entry_link),
                            source=source,
                            title=entry_title,
                            link=entry_link,
                            description=clean_description(raw_desc, entry_title),
                            published=published_str,
                            fetched_at=now.isoformat(),
                        )
                    )

                logging.info(f"Parsed {len(parsed.entries)} entries from '{source}'.")

            except Exception as e:
                logging.error(f"Error fetching feed '{source}' ({url}): {e}")
                continue

        if items:
            upsert_items(client, items)
            logging.info(f"Upserted {len(items)} items for '{category_title}'.")

    delete_old_items(client)
    logging.info("RSS fetch complete.")
