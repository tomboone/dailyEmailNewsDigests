"""Configuration for dailyemailnewsdigests."""

import os


def _require_env(name: str) -> str:
    """Return the value of a required environment variable, or raise."""
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Required environment variable '{name}' is not set")
    return value


# Schedules
DIGESTS_NCRON: str = os.getenv("DIGESTS_NCRON", "0 0 10 * * *")
RSS_FETCH_NCRON: str = os.getenv("RSS_FETCH_NCRON", "0 */5 * * * *")

# Email
SENDER: str = _require_env("SENDER")
SMTP_SERVER: str = _require_env("SMTP_SERVER")
SMTP_USER: str = _require_env("SMTP_USER")
SMTP_PWD: str = _require_env("SMTP_PWD")
SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
DIGEST_NAME: str = os.getenv("DIGEST_NAME", "News Digest")

# Azure Storage
AZURE_STORAGE_CONNECTION_STRING: str = _require_env("AZURE_STORAGE_CONNECTION_STRING")
