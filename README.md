# Daily Email News Digests

An Azure Function App that fetches RSS feeds on a schedule and sends a daily email digest with the latest articles, grouped by category.

## Features

* **RSS Feed Aggregation:** Fetches and parses RSS feeds every 5 minutes, storing articles in Azure Table Storage.
* **Daily Digest Email:** Sends a single styled HTML email per recipient with articles grouped into sections by category.
* **Deduplication:** Articles are deduplicated by URL, so the same article from multiple fetches is only included once.
* **Automatic Cleanup:** Items older than 7 days are automatically removed from storage.
* **Configurable:** Feed sources, categories, schedules, and email settings are all configurable.

## Architecture

Two Azure Functions timer triggers:

* **`fetch_rss_feeds`** — Runs every 5 minutes. Parses RSS feeds defined in `feeds.json` and upserts new articles into Azure Table Storage.
* **`digest_email`** — Runs daily at 10:00 AM. Queries articles from the last 24 hours, builds a styled HTML email, and sends it via SMTP.

## Getting Started

### Prerequisites

* Python 3.12
* [Poetry](https://python-poetry.org/) for dependency management
* [Azure Functions Core Tools](https://learn.microsoft.com/en-us/azure/azure-functions/functions-run-local)
* [Azurite](https://learn.microsoft.com/en-us/azure/storage/common/storage-use-azurite) for local Azure Storage emulation

### Installation

1. **Clone the repository:**
    ```bash
    git clone https://github.com/tomboone/dailyEmailNewsDigests.git
    cd dailyEmailNewsDigests
    ```

2. **Install dependencies:**
    ```bash
    poetry config virtualenvs.in-project true
    poetry install
    ```

3. **Install pre-commit hooks:**
    ```bash
    poetry run pre-commit install
    ```

4. **Configure local settings:** Create a `local.settings.json` file in the project root (ignored by Git):
    ```json
    {
      "IsEncrypted": false,
      "Values": {
        "AzureWebJobsStorage": "UseDevelopmentStorage=true",
        "FUNCTIONS_WORKER_RUNTIME": "python",
        "WEBSITE_TIME_ZONE": "Eastern Standard Time",
        "SENDER": "sender@example.com",
        "SMTP_SERVER": "smtp.example.com",
        "SMTP_USER": "your_smtp_user",
        "SMTP_PWD": "your_smtp_password",
        "SMTP_PORT": "587",
        "AZURE_STORAGE_CONNECTION_STRING": "UseDevelopmentStorage=true",
        "DIGEST_NAME": "News Digest"
      }
    }
    ```

### Running Locally

1. **Start Azurite** (required for Table Storage and timer trigger scheduling):
    ```bash
    azurite
    ```

2. **Start the Function App:**
    ```bash
    func start
    ```

### Development

```bash
poetry run pytest              # Run tests
poetry run ruff check --fix    # Lint and auto-fix
poetry run ruff format         # Format code
poetry run pyright             # Type check
```

## Configuration

### Environment Variables

| Variable | Required | Default | Description |
|---|---|---|---|
| `SENDER` | Yes | — | "From" email address |
| `SMTP_SERVER` | Yes | — | SMTP server hostname |
| `SMTP_USER` | Yes | — | SMTP username |
| `SMTP_PWD` | Yes | — | SMTP password |
| `AZURE_STORAGE_CONNECTION_STRING` | Yes | — | Azure Table Storage connection string |
| `SMTP_PORT` | No | `587` | SMTP server port |
| `DIGESTS_NCRON` | No | `0 0 10 * * *` | Digest email schedule (NCronTab) |
| `RSS_FETCH_NCRON` | No | `0 */5 * * * *` | RSS fetch schedule (NCronTab) |
| `DIGEST_NAME` | No | `News Digest` | Email subject and heading |
| `WEBSITE_TIME_ZONE` | No | UTC | Timezone for schedules (e.g., `Eastern Standard Time`) |

### Feed Configuration

RSS feeds are configured in `src/dailyemailnewsdigests/feeds.json`. Each category contains a list of feed sources with a display name and URL.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

Copyright (c) 2025 Tom Boone.
