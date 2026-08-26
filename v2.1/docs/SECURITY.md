# Security and privacy

The public showcase intentionally excludes:

- broker authentication implementation (`f3.py`)
- API keys, access/refresh tokens and secrets
- Telegram bot tokens and chat IDs
- user/account identifiers
- local VM-specific absolute paths
- `.env` files
- runtime locks and state files
- raw option-chain snapshots and private historical datasets
- paper/live trade ledgers and execution audit files
- Python bytecode, caches, backup archives and diagnostic ZIPs

Only `.env.example` is included, with non-secret configuration placeholders. Secrets should be injected through environment variables or a secret manager and never committed.
