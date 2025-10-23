from __future__ import annotations

import pytest

from risk.filters import RiskConfig, RiskFilter, RiskViolation


def test_risk_filter_blocks_position() -> None:
    """Risk filter should prevent positions that exceed configured limits."""
    config = RiskConfig(max_position=5, max_notional=1000.0, max_daily_trades=1)
    risk = RiskFilter(config)

    with pytest.raises(RiskViolation):
        risk.validate({"quantity": 10}, current_position=0, price=10.0)


def test_risk_filter_allows_within_limits() -> None:
    """Risk filter allows trades within size and notional thresholds."""
    config = RiskConfig(max_position=5, max_notional=1000.0, max_daily_trades=2)
    risk = RiskFilter(config)

    risk.validate({"quantity": 2}, current_position=0, price=10.0)
    risk.validate({"quantity": -2}, current_position=2, price=10.0)
