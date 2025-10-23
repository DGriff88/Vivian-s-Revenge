"""Risk management filters for validating orders."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict


class RiskViolation(Exception):
    """Raised when risk checks fail."""


@dataclass
class RiskConfig:
    """Configuration for risk tolerances enforced by the filter."""

    max_position: int
    max_notional: float
    max_daily_trades: int


class RiskFilter:
    """Apply configured risk rules to candidate orders."""

    def __init__(self, config: RiskConfig) -> None:
        """Store the risk configuration and reset counters."""
    def __init__(self, config: RiskConfig) -> None:
        self.config = config
        self._daily_trade_count = 0

    def reset_daily_counters(self) -> None:
        """Reset the accumulated count of trades for the current day."""
        self._daily_trade_count = 0

    def validate(self, order: Dict[str, float], current_position: int, price: float) -> None:
        """Validate an order against configured risk limits."""
        projected_position = current_position + int(order.get("quantity", 0))
        projected_notional = abs(projected_position * price)

        if abs(projected_position) > self.config.max_position:
            raise RiskViolation("Projected position exceeds max_position limit")

        if projected_notional > self.config.max_notional:
            raise RiskViolation("Projected notional exceeds max_notional limit")

        if self._daily_trade_count >= self.config.max_daily_trades:
            raise RiskViolation("Exceeded maximum daily trades")

        self._daily_trade_count += 1
