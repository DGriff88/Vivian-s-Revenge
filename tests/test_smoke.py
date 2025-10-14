from __future__ import annotations

import json
from pathlib import Path
from typing import Dict

from cli.main import run_pipeline


def test_end_to_end_smoke(monkeypatch, tmp_path: Path) -> None:
    sample_payload: Dict[str, object] = {
        "prices": [
            {"timestamp": "2024-01-01T09:30:00Z", "open": 1, "high": 1.2, "low": 0.9, "close": 1.1, "volume": 1000},
            {"timestamp": "2024-01-01T09:31:00Z", "open": 1.1, "high": 1.3, "low": 1.0, "close": 1.2, "volume": 1200},
            {"timestamp": "2024-01-01T09:32:00Z", "open": 1.2, "high": 1.4, "low": 1.1, "close": 1.3, "volume": 1500},
            {"timestamp": "2024-01-01T09:33:00Z", "open": 1.3, "high": 1.5, "low": 1.2, "close": 1.4, "volume": 1500},
            {"timestamp": "2024-01-01T09:34:00Z", "open": 1.4, "high": 1.6, "low": 1.3, "close": 1.5, "volume": 1700},
        ]
    }

    def fake_fetch(self, symbol: str, start: str, end: str):  # pragma: no cover - simple stub
        return sample_payload

    monkeypatch.setenv("AUDIT_LOG_PATH", str(tmp_path / "audit.log"))
    monkeypatch.setattr("scrapers.market_data.MarketDataScraper.get_intraday_prices", fake_fetch)

    run_pipeline("SPY", tmp_path)

    audit_log = tmp_path / "audit.log"
    assert audit_log.exists()
    with audit_log.open() as handle:
        entries = [json.loads(line) for line in handle]
    assert entries
    assert entries[0]["status"] == "filled"
    assert entries[0]["symbol"] == "SPY"
