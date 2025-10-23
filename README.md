# Vivian's Revenge Trading Scaffold

This repository contains a modular, safety-first scaffold for building automated trading
workflows. The system is intentionally dry-run by default and splits responsibilities
into dedicated modules for scraping, normalization, signal generation, risk filtering,
and execution.

## Features

- **Scrapers**: `scrapers/` fetches market data with caching, retry/backoff, robots.txt
  compliance, and rate limiting.
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
- **CLI**: `cli/main.py` orchestrates an end-to-end mock pipeline and emits JSON
  summaries covering the strategy spec, dry-run result, and live-execution
  gating requirements.
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

## Quick Orientation

- **Workflow**: The CLI drives the process end-to-end: scrape → normalize → signal →
  risk check → mock execution.
- **Data**: In the absence of a `DATA_API_KEY`, the CLI automatically falls back to
  a bundled sample dataset so you can experiment without credentials.
- **Extensibility**: Swap out any module (e.g., replace the scraper or signal) by
  editing the dedicated package and running the tests.
## Quickstart

Clone the repository, set up a virtual environment, install dependencies, and run
the mock pipeline end-to-end.

```bash
git clone https://github.com/your-org/vivian-s-revenge.git
cd vivian-s-revenge
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python -m cli.main SPY --data-dir .vivian_data
```

The command above runs the entire flow in mock mode, caching any downloaded market
data, generating signals, enforcing risk rules, and writing audit logs to
`audit_logs.jsonl` by default.

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
When no API credentials are available the bundled sample data located at
`scrapers/sample_data/intraday_sample.json` is used so the run succeeds offline.

## Customising for Your Data or Broker

1. **Scraper**: Update `scrapers/market_data.py` with your provider's endpoint and
   authentication scheme. All secrets should be provided via environment variables
   as demonstrated with `DATA_API_KEY`.
2. **Signals**: Implement new signal functions in `signals/` that return a `SignalResult`.
3. **Risk**: Tune `RiskConfig` limits or extend `RiskFilter` with additional checks.
4. **Executor**: Integrate a real broker by implementing `executor/live.py` once you
   have met the gating requirements and obtained human approval.
5. **CLI**: Adjust `cli/main.py` to orchestrate any new modules or to pass additional
   context (e.g., portfolio state) into the pipeline.
The command prints a JSON document with:

1. **`strategy_spec`** – a machine-readable description of the momentum leg(s).
2. **`dry_run`** – simulated execution details or the reason a trade was skipped.
3. **`live_execution`** – explicit confirmation requirements before live trading
   can be enabled.

The pipeline operates in mock mode unless you explicitly opt into live execution
(see below).

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

Pytest covers individual modules and includes a smoke test that exercises the CLI in
mock mode with deterministic sample data.

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
