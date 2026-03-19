"""Blueprint for building and sending daily digest emails."""

import logging
from datetime import datetime
from typing import Any

import azure.functions as func

import src.dailyemailnewsdigests.config as config
from src.dailyemailnewsdigests.email_builder import (
    build_html_email,
    build_plain_text_email,
    send_smtp_email,
)
from src.dailyemailnewsdigests.storage import get_table_client, mark_items_sent, query_unsent_items
from src.dailyemailnewsdigests.utils import load_feeds

bp: func.Blueprint = func.Blueprint()


# noinspection PyUnusedLocal
@bp.timer_trigger(
    schedule=config.DIGESTS_NCRON,
    arg_name="digest_timer",
    run_on_startup=False,
)
def digest_email(digest_timer: func.TimerRequest) -> None:
    """Timer trigger to query stored items and send a digest email."""
    feeds_config = load_feeds()
    recipient: str = feeds_config["recipient"]
    client = get_table_client()

    sections: list[dict[str, Any]] = []
    all_items: list[dict[str, Any]] = []

    for category in feeds_config["categories"]:
        category_title: str = category["title"]
        items = query_unsent_items(client, category_title)

        if not items:
            logging.info(f"No unsent items for '{category_title}'. Skipping section.")
            continue

        items.sort(key=lambda x: x.get("published", ""), reverse=True)
        logging.info(f"Found {len(items)} unsent items for '{category_title}'.")
        sections.append({"title": category_title, "items": items})
        all_items.extend(items)

    if not sections:
        logging.info("No unsent items found for any category. No email sent.")
        return

    subject = config.DIGEST_NAME
    date_str = datetime.now().strftime("%B %d, %Y")

    html_body = build_html_email(subject, date_str, sections)
    text_body = build_plain_text_email(subject, sections)

    try:
        send_smtp_email(
            subject=subject,
            text_body=text_body,
            html_body=html_body,
            sender=config.SENDER,
            recipient=recipient,
        )
        mark_items_sent(client, all_items)
        logging.info(f"Successfully sent digest email to {recipient} ({len(all_items)} items).")
    except Exception as e:
        logging.error(f"Unable to send digest email to {recipient}: {e}")
