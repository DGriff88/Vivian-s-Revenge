"""Data models for order execution."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Dict


def _current_time() -> datetime:
    return datetime.now(UTC)


@dataclass
class OrderRequest:
    symbol: str
    side: str
    quantity: int
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class ExecutionReport:
    order: OrderRequest
    status: str
    filled_quantity: int
    average_price: float
    timestamp: datetime = field(default_factory=_current_time)
