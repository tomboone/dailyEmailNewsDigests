"""Shared utility functions for dailyemailnewsdigests."""

import json
from pathlib import Path
from typing import Any


def clean_description(text: str, title: str) -> str:
    """Clean article description text by removing common truncation markers.

    Args:
        text: The description text to clean.
        title: The article title (removed if it appears as a prefix).

    Returns:
        The cleaned text.
    """
    separators = [title, "[\u2026]", "...Keep reading", "(...)"]
    for sep in separators:
        if sep in text:
            text = text.split(sep, 1)[0]
    return text.strip()


def load_feeds() -> dict[str, Any]:
    """Load the feed configuration from feeds.json.

    Returns:
        Dict with 'recipient' and 'categories' keys.
    """
    feeds_path = Path(__file__).parent / "feeds.json"
    with open(feeds_path) as f:
        return json.load(f)
