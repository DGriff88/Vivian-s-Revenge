"""Command line interface for running the dry-run trading pipeline."""

from __future__ import annotations

import argparse
import logging
from datetime import datetime, timedelta, timezone
from pathlib import Path

from executor.mock import MockExecutor
from executor.models import OrderRequest
from normalizers.price import normalize_ohlc_rows
from risk.filters import RiskConfig, RiskFilter, RiskViolation
from scrapers.market_data import MarketDataScraper, ScraperConfig
from signals.momentum import momentum_signal

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_pipeline(symbol: str, data_dir: Path) -> None:
    config = ScraperConfig(
        base_url="https://example.com/api/",
        endpoint="intraday",
        cache_dir=data_dir / "cache",
        cache_ttl_seconds=5,
    )
    scraper = MarketDataScraper(config)

    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=1)
    raw = scraper.get_intraday_prices(symbol, start.isoformat(), end.isoformat())
    normalized = normalize_ohlc_rows(raw["prices"])
    closes = [row["close"] for row in normalized]
    signal = momentum_signal(closes)

    logger.info("Momentum signal for %s: %s", symbol, signal.signal)

    risk_filter = RiskFilter(RiskConfig(max_position=10, max_notional=10000.0, max_daily_trades=5))
    desired_quantity = signal.signal
    if desired_quantity == 0:
        logger.info("No trade signal generated")
        return

    order = {"symbol": symbol, "quantity": desired_quantity}
    try:
        risk_filter.validate(order, current_position=0, price=closes[-1])
    except RiskViolation as exc:
        logger.warning("Trade blocked by risk filter: %s", exc)
        return

    executor = MockExecutor()
    report = executor.execute(
        OrderRequest(symbol=symbol, side="buy" if desired_quantity > 0 else "sell", quantity=abs(desired_quantity)),
        price=closes[-1],
    )
    logger.info("Mock execution report: %s", report)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Vivian's Revenge dry-run pipeline")
    parser.add_argument("symbol", help="Ticker symbol to evaluate")
    parser.add_argument("--data-dir", type=Path, default=Path(".vivian_data"), help="Working data directory")
    args = parser.parse_args()

    run_pipeline(args.symbol, args.data_dir)


if __name__ == "__main__":
    main()
