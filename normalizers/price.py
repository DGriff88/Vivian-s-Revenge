"""Data normalization helpers for price series."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable, List, Mapping


def normalize_ohlc_rows(rows: Iterable[Mapping[str, object]]) -> List[dict]:
    """Normalize raw OHLC rows into canonical format.

    Each row must include timestamp (ISO string), open/high/low/close, and volume.
    Values are converted to floats and timestamps parsed into aware UTC datetimes.
    """

    normalized = []
    for row in rows:
        try:
            timestamp = datetime.fromisoformat(str(row["timestamp"]).replace("Z", "+00:00"))
            normalized.append(
                {
                    "timestamp": timestamp,
                    "open": float(row["open"]),
                    "high": float(row["high"]),
                    "low": float(row["low"]),
                    "close": float(row["close"]),
                    "volume": float(row["volume"]),
                }
            )
        except (KeyError, ValueError, TypeError) as exc:
            raise ValueError(f"Invalid row for normalization: {row}") from exc
    normalized.sort(key=lambda item: item["timestamp"])
    return normalized
