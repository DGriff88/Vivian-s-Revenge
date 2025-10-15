# Vivian's Revenge Trading Scaffold

This repository contains a modular, safety-first scaffold for building automated trading
workflows. The system is intentionally dry-run by default and splits responsibilities
into dedicated modules for scraping, normalization, signal generation, risk filtering,
and execution.

## Features

- **Scrapers**: `scrapers/` fetches market data with caching, retry/backoff, robots.txt
  compliance, and rate limiting. Configure scraper `base_url` values with the full API
  root (including any path segments) and a trailing slash, for example
  `https://example.com/api/`, so endpoints join as relative paths while robots.txt is
  checked against `/endpoint/`.
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

## Environment Variables

Environment variables must be configured via `.env` or shell exports. See `env.example`
for the complete list of required names.
