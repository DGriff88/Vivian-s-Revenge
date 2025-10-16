from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from urllib import robotparser

import pytest

from scrapers.market_data import MarketDataScraper, ScraperConfig


class DummyResponse:
    def __init__(self, payload: Dict[str, Any]) -> None:
        self._payload = payload
        self.text = "User-agent: *\nAllow: /intraday/"

    def json(self) -> Dict[str, Any]:
        return self._payload

    def raise_for_status(self) -> None:  # pragma: no cover - simple stub
        return None


class DummySession:
    def __init__(self, response: DummyResponse) -> None:
        self.response = response
        self.calls = []

    def get(self, url: str, **kwargs: Any) -> DummyResponse:  # pragma: no cover - trivial
        self.calls.append((url, kwargs))
        return self.response


@pytest.fixture
def allow_all_parser() -> robotparser.RobotFileParser:
    parser = robotparser.RobotFileParser()
    parser.parse(["User-agent: *", "Allow: /"])
    return parser


def test_scraper_uses_cache(tmp_path: Path, allow_all_parser: robotparser.RobotFileParser) -> None:
    payload = {"prices": [{"timestamp": "2024-01-01T09:30:00Z", "open": 1, "high": 1, "low": 1, "close": 1, "volume": 1}]}
    session = DummySession(DummyResponse(payload))
    config = ScraperConfig(base_url="https://example.com", endpoint="intraday", cache_dir=tmp_path)
    scraper = MarketDataScraper(config, session=session, robot_parser=allow_all_parser)

    first = scraper.get_intraday_prices("SPY", "start", "end")
    second = scraper.get_intraday_prices("SPY", "start", "end")

    assert first == payload
    assert second == payload
    assert len(session.calls) == 1  # cache hit on second call


def test_cache_key_sanitizes_invalid_characters(
    tmp_path: Path, allow_all_parser: robotparser.RobotFileParser
) -> None:
    payload = {"prices": []}
    session = DummySession(DummyResponse(payload))
    config = ScraperConfig(base_url="https://example.com", endpoint="intraday", cache_dir=tmp_path)
    scraper = MarketDataScraper(config, session=session, robot_parser=allow_all_parser)

    scraper.get_intraday_prices("SPY", "2024-01-01T09:30:00Z", "2024-01-01T16:00:00Z")

    cache_files = list(tmp_path.glob("*.json"))
    assert cache_files, "Expected a cache file to be created"
    assert all(":" not in path.name for path in cache_files)


def test_scraper_respects_robots(tmp_path: Path) -> None:
    parser = robotparser.RobotFileParser()
    parser.parse(["User-agent: *", "Disallow: /intraday/"])
    config = ScraperConfig(base_url="https://example.com", endpoint="intraday", cache_dir=tmp_path)
    scraper = MarketDataScraper(config, session=DummySession(DummyResponse({})), robot_parser=parser)

    with pytest.raises(PermissionError):
        scraper.get_intraday_prices("SPY", "start", "end")
