# Vivian's Revenge Onboarding Guide

Welcome to Vivian's Revenge, a modular, safety-first scaffold for automated trading research. This guide orients you around the repository layout, critical design patterns, and suggested next steps for new contributors.

## High-Level Architecture

The system is intentionally split into clear layers that mirror a typical trading workflow:

1. **Data Acquisition (`scrapers/`)** – Responsible for fetching market data from external APIs.
2. **Normalization (`normalizers/`)** – Converts raw API payloads into canonical OHLC structures.
3. **Signal Generation (`signals/`)** – Houses trading models; currently focuses on momentum crossovers.
4. **Risk Management (`risk/`)** – Applies hard limits to proposed trades before anything is executed.
5. **Execution (`executor/`)** – Provides mock and guarded live execution paths with audit logging.
6. **Command Line Interface (`cli/`)** – Orchestrates an end-to-end dry-run using the modules above.
7. **Automated Tests (`tests/`)** – Pytest suite covering scrapers, normalization, signals, risk, and a smoke test for the pipeline.

### Data Flow Overview

```
MarketDataScraper -> normalize_ohlc_rows -> momentum_signal -> RiskFilter -> Executor
```

The CLI composes these pieces to form a reproducible, testable mock trading run.

## Module Deep Dive

### Scrapers (`scrapers/market_data.py`)
- **`ScraperConfig`** – Dataclass bundling base URL, endpoint, caching, rate limits, retry policy, and user-agent.
- **`MarketDataScraper`** – Fetches intraday prices while respecting `robots.txt`, rate limits, and cache TTL. API keys are sourced from `DATA_API_KEY` in the environment. Caches responses to disk for reuse across runs.

### Normalizers (`normalizers/price.py`)
- **`normalize_ohlc_rows`** – Validates and coerces raw price rows into sorted OHLC dictionaries with timezone-aware timestamps.

### Signals (`signals/momentum.py`)
- **`momentum_signal`** – Computes a short vs. long moving-average crossover and returns a `SignalResult` dataclass containing the decision (+1/-1/0) plus the computed averages.

### Risk (`risk/filters.py`)
- **`RiskFilter`** – Enforces position, notional, and daily-trade limits defined by `RiskConfig`. Raises `RiskViolation` when constraints fail.

### Execution (`executor/`)
- **`MockExecutor`** – Default path, always on dry-run. Simulates fills and appends JSONL audit entries. Output location configurable via `AUDIT_LOG_PATH`.
- **`LiveExecutor`** – Guarded by `EXECUTE_LIVE=true` *and* a structured `APPROVAL_JSON`. Still raises `NotImplementedError` to prevent accidental real trades.
- **`OrderRequest`/`ExecutionReport`** – Dataclasses representing orders and resulting execution reports.

### CLI (`cli/main.py`)
- `run_pipeline` composes the modules: downloads one hour of intraday data, normalizes it, computes the momentum signal, runs risk checks, and executes in mock mode if a trade is warranted.
- CLI entry point exposes `python -m cli.main <symbol> --data-dir <path>`.

### Tests (`tests/`)
- **Unit Tests** – Cover scrapers (cache & robots compliance), signals (basic validation), and risk filters.
- **End-to-End Smoke Test** – `test_smoke.py` patches the scraper, runs the full CLI pipeline, and verifies the audit log output in mock mode.

## Configuration & Environment

- `env.example` lists required environment variable *names* (e.g., `DATA_API_KEY`, `AUDIT_LOG_PATH`). Populate these in a `.env` file or export them in your shell.
- All secrets are read via `os.getenv(...)`; never hard-code keys.
- Mock execution is default. Live trading is intentionally blocked without explicit human approval provided through environment variables.

## Recommended Next Steps

1. **Run the Pipeline:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   python -m cli.main SPY --data-dir .vivian_data
   ```
2. **Explore Tests:**
   ```bash
   pytest -q
   ```
3. **Extend Signals:** Try building alternative indicators (RSI, mean reversion) within `signals/`, following the same dataclass pattern.
4. **Enhance Risk Controls:** Add position decay, instrument whitelists, or P&L tracking to `risk/`.
5. **Integrate New Data Sources:** Implement additional scrapers under `scrapers/` that respect caching, throttling, and robots rules.
6. **Improve Observability:** Expand audit logging, add metrics exporters, or integrate structured logging.

## Learning Resources

- **Python Dataclasses:** Crucial for the configuration and model types across modules.
- **Pytest Fixtures & Monkeypatching:** Used extensively for isolated, deterministic tests.
- **Requests & Rate Limiting:** Understand retry strategies and robots.txt compliance when working on scrapers.

Welcome aboard! Reach out in the project chat with questions or proposals before implementing major features.
