"""Strategy specification helpers for momentum signals."""

from __future__ import annotations

from typing import Dict, List


def build_momentum_strategy_spec(
    symbol: str,
    closes: List[float],
    signal_value: int,
    short_window: int,
    long_window: int,
) -> Dict[str, object]:
    """Create a JSON-serializable spec describing the momentum strategy legs."""

    if long_window <= short_window:
        raise ValueError("long_window must be greater than short_window")

    side = "buy" if signal_value > 0 else "sell" if signal_value < 0 else "flat"
    quantity = abs(signal_value)
    legs = []
    if quantity:
        legs.append(
            {
                "symbol": symbol,
                "side": side,
                "quantity": quantity,
                "order_type": "market",
            }
        )

    return {
        "strategy": "momentum_crossover",
        "net_delta": signal_value,
        "parameters": {
            "short_window": short_window,
            "long_window": long_window,
        },
        "legs": legs,
        "data_points": len(closes),
        "notes": "Dry-run spec generated for human review prior to live execution.",
    }
