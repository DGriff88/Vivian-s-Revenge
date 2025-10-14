# Vivian's Revenge Trading Scaffold

This repository contains a modular, safety-first scaffold for building automated trading
workflows. The system is intentionally dry-run by default and splits responsibilities
into dedicated modules for scraping, normalization, signal generation, risk filtering,
and execution.

## Features

- **Scrapers**: `scrapers/` fetches market data with caching, retry/backoff, robots.txt
  compliance, and rate limiting.
- **Normalizers**: `normalizers/` standardizes raw payloads into clean OHLC structures.
- **Signals**: `signals/` houses momentum-based signal calculation utilities.
- **Risk**: `risk/` enforces configurable position, notional, and trade-count limits.
- **Executor**: `executor/mock.py` simulates fills while writing JSONL audit logs.
  `executor/live.py` introduces strict gating for any real execution.
- **CLI**: `cli/main.py` orchestrates an end-to-end mock pipeline.
- **Tests**: `tests/` includes unit coverage for each subsystem plus a smoke test for the
  pipeline.

## Requirements

- Python 3.10+
- Dependencies listed in `requirements.txt` or installable via the `pyproject.toml`.

## Installation

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Running the Mock Pipeline

```bash
python -m cli.main SPY --data-dir .vivian_data
```

The pipeline operates in mock mode, downloading (or using cached) market data, generating
signals, enforcing risk checks, and writing audit logs to `audit_logs.jsonl` by default.

## Live Execution Safety

Live execution is disabled unless both environment variables are set:

- `EXECUTE_LIVE=true`
- `APPROVAL_JSON` containing a serialized human approval record.

Even when provided, the live executor currently raises `NotImplementedError` as an
additional safeguard.

## Testing

```bash
pytest
```

## Pushing Changes and Merging Branches

1. Commit your work locally:
   ```bash
   git add .
   git commit -m "Describe your change"
   ```
2. Push the branch to the remote (replace `my-branch` with your branch name):
   ```bash
   git push origin my-branch
   ```
3. Open a pull request in your Git hosting provider and request any required reviews.
4. Once the pull request is approved and checks pass, merge it using the platform's UI
   (e.g., **Merge pull request** button) or from the command line:
   ```bash
   git checkout main
   git pull origin main
   git merge my-branch
   git push origin main
   ```

## Environment Variables

Environment variables must be configured via `.env` or shell exports. See `env.example`
for the complete list of required names.
