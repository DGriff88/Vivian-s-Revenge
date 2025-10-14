from __future__ import annotations

import pytest

from signals.momentum import SignalResult, momentum_signal


def test_momentum_signal_positive() -> None:
    data = [1, 2, 3, 4, 5]
    result = momentum_signal(data, short_window=2, long_window=4)
    assert isinstance(result, SignalResult)
    assert result.signal == 1
    assert result.short_ma > result.long_ma


def test_momentum_signal_requires_sufficient_data() -> None:
    with pytest.raises(ValueError):
        momentum_signal([1, 2], short_window=2, long_window=3)
