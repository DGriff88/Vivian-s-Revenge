"""Signal generation logic for momentum-based strategies."""

from __future__ import annotations

from dataclasses import dataclass
from statistics import mean
from typing import Iterable, List


@dataclass
class SignalResult:
    signal: int
    short_ma: float
    long_ma: float


def _moving_average(series: List[float]) -> float:
    if not series:
        raise ValueError("Series cannot be empty for moving average computation")
    return mean(series)


def momentum_signal(closing_prices: Iterable[float], short_window: int = 3, long_window: int = 5) -> SignalResult:
    """Compute a simple momentum signal using moving average crossover."""
    prices = list(closing_prices)
    if long_window <= short_window:
        raise ValueError("long_window must be greater than short_window")
    if len(prices) < long_window:
        raise ValueError("Not enough price data to compute momentum signal")

    short_ma = _moving_average(prices[-short_window:])
    long_ma = _moving_average(prices[-long_window:])

    if short_ma > long_ma:
        signal_value = 1
    elif short_ma < long_ma:
        signal_value = -1
    else:
        signal_value = 0

    return SignalResult(signal=signal_value, short_ma=short_ma, long_ma=long_ma)
