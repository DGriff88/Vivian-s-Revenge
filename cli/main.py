"""Command line interface for running the dry-run trading pipeline."""

from __future__ import annotations

import argparse
import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Dict, Optional

from executor.mock import MockExecutor
from executor.models import OrderRequest
from normalizers.price import normalize_ohlc_rows
from risk.filters import RiskConfig, RiskFilter, RiskViolation
from scrapers.market_data import MarketDataScraper, ScraperConfig
from signals.momentum import momentum_signal
from signals.spec import build_momentum_strategy_spec

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def run_pipeline(symbol: str, data_dir: Path) -> None:
    """Run the end-to-end pipeline in mock mode for the provided symbol."""
    data_dir.mkdir(parents=True, exist_ok=True)
def _format_confirmation_requirements() -> Dict[str, object]:
    return {
        "required_env": ["EXECUTE_LIVE=true", "APPROVAL_JSON"],
        "human_action": "Review dry-run outputs and provide signed approval JSON before enabling live execution.",
        "status": "live_execution_blocked",
    }


def run_pipeline(symbol: str, data_dir: Path) -> Dict[str, object]:
    short_window = 3
    long_window = 5
    config = ScraperConfig(
        base_url="https://example.com/api/",
        endpoint="intraday",
        cache_dir=data_dir / "cache",
        cache_ttl_seconds=5,
    )
    scraper = MarketDataScraper(config)

    end = datetime.now(timezone.utc)
    start = end - timedelta(hours=1)
    if os.getenv("DATA_API_KEY"):
        raw = scraper.get_intraday_prices(symbol, start.isoformat(), end.isoformat())
    else:
        logger.warning("DATA_API_KEY not set; using bundled sample data")
        raw = _load_sample_payload()
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


def _load_sample_payload() -> Dict[str, Any]:
    """Load the bundled sample intraday dataset when no API credentials are available."""
    sample_path = Path(__file__).resolve().parent.parent / "scrapers" / "sample_data" / "intraday_sample.json"
    with sample_path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def main() -> None:
    """Entrypoint for command line execution."""
    raw = scraper.get_intraday_prices(symbol, start.isoformat(), end.isoformat())
    normalized = normalize_ohlc_rows(raw["prices"])
    closes = [row["close"] for row in normalized]
    signal = momentum_signal(closes, short_window=short_window, long_window=long_window)

    logger.info("Momentum signal for %s: %s", symbol, signal.signal)

    strategy_spec = build_momentum_strategy_spec(
        symbol=symbol,
        closes=closes,
        signal_value=signal.signal,
        short_window=short_window,
        long_window=long_window,
    )
    logger.info("Strategy spec: %s", json.dumps(strategy_spec))

    risk_filter = RiskFilter(RiskConfig(max_position=10, max_notional=10000.0, max_daily_trades=5))
    desired_quantity = signal.signal
    dry_run: Dict[str, Optional[object]]

    if desired_quantity == 0:
        dry_run = {
            "status": "no_trade_signal",
            "reason": "Momentum crossover produced a flat signal.",
        }
        logger.info("No trade signal generated")
    else:
        order_payload = {"symbol": symbol, "quantity": desired_quantity}
        try:
            risk_filter.validate(order_payload, current_position=0, price=closes[-1])
        except RiskViolation as exc:
            dry_run = {
                "status": "blocked_by_risk",
                "reason": str(exc),
            }
            logger.warning("Trade blocked by risk filter: %s", exc)
        else:
            executor = MockExecutor()
            order_request = OrderRequest(
                symbol=symbol,
                side="buy" if desired_quantity > 0 else "sell",
                quantity=abs(desired_quantity),
            )
            report = executor.execute(order_request, price=closes[-1])
            dry_run = {
                "status": "filled",
                "average_price": report.average_price,
                "filled_quantity": report.filled_quantity,
                "timestamp": report.timestamp.isoformat(),
            }
            logger.info("Mock execution report: %s", report)

    confirmation_requirements = _format_confirmation_requirements()
    summary = {
        "strategy_spec": strategy_spec,
        "dry_run": dry_run,
        "live_execution": confirmation_requirements,
    }
    logger.info("Live execution remains disabled: %s", json.dumps(confirmation_requirements))
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Vivian's Revenge dry-run pipeline")
    parser.add_argument("symbol", help="Ticker symbol to evaluate")
    parser.add_argument("--data-dir", type=Path, default=Path(".vivian_data"), help="Working data directory")
    args = parser.parse_args()

    run_pipeline(args.symbol, args.data_dir)
    result = run_pipeline(args.symbol, args.data_dir)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
