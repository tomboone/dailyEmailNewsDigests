# Daily Email News Digests

Azure Function app that fetches RSS feeds and sends daily email digests. Python 3.12, deployed to Azure via GitHub Actions.

## Architecture

Two timer-triggered Azure Functions registered as blueprints in `function_app.py`:

- **`bp_rss_fetcher`** — runs every 5 minutes, parses RSS feeds defined in `feeds.json`, stores items in Azure Table Storage
- **`bp_digests`** — runs daily at 10 AM, queries recent items from storage, builds a styled HTML email, sends via SMTP

Shared modules under `src/dailyemailnewsdigests/`:
- `config.py` — env var loading with `_require_env()` validation
- `storage.py` — Azure Table Storage operations (`RssItemEntity` TypedDict, upsert/query/cleanup)
- `email_builder.py` — HTML + plain text email construction, SMTP sending
- `utils.py` — `clean_description()`, `load_feeds()`
- `feeds.json` — feed URLs and categories (F1, MotoGP, INDYCAR)

## Commands

```bash
poetry run pytest              # Run tests
poetry run ruff check --fix    # Lint
poetry run ruff format         # Format
poetry run pyright             # Type check
```

Pre-commit hooks run all four automatically on commit.

## Conventions

- Imports use full `src.dailyemailnewsdigests.*` paths (not relative)
- Blueprint files prefixed `bp_`
- Type hints: use `Optional[X]` / `Union[X, Y]`, not pipe syntax
- No `from __future__ import annotations`
- Ruff line length: 100
- Pyright: standard mode

## Environment Variables

**Required:** `SENDER`, `SMTP_SERVER`, `SMTP_USER`, `SMTP_PWD`, `AZURE_STORAGE_CONNECTION_STRING`

**Optional (with defaults):** `DIGESTS_NCRON` (daily 10 AM), `RSS_FETCH_NCRON` (every 5 min), `SMTP_PORT` (587), `DIGEST_NAME` ("News Digest")

## Deployment

Push to `main` triggers a three-stage GitHub Actions workflow: test → Terraform → deploy. Authenticated via OIDC (workload identity federation). Environment: `prod` (requires approval).

## Infrastructure

Terraform files in `infra/`. Creates resource group, storage account, Key Vault, and Function App. References an existing App Service Plan via data source.

```bash
cd infra
terraform init -backend-config="resource_group_name=..." -backend-config="storage_account_name=..." -backend-config="container_name=..." -backend-config="key=dailyemailnewsdigests.tfstate"
terraform plan
terraform validate
terraform fmt -check -recursive
```

Secrets managed via Azure Key Vault with Key Vault references in Function App app settings. State stored in a pre-existing Azure Storage account.

### GitHub Secrets (OIDC)

`AZURE_CLIENT_ID`, `AZURE_TENANT_ID`, `AZURE_SUBSCRIPTION_ID`

### GitHub Secrets (Terraform State)

`TF_STATE_RESOURCE_GROUP`, `TF_STATE_STORAGE_ACCOUNT`, `TF_STATE_CONTAINER`
