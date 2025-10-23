from __future__ import annotations

from pathlib import Path
from typing import Any, Dict
from urllib import robotparser

import pytest
import requests

from scrapers.market_data import MarketDataScraper, ScraperConfig


class DummyResponse:
    """Minimal response stub for the scraper tests."""

    def __init__(self, payload: Dict[str, Any]) -> None:
        """Store the payload and expose a permissive robots body."""
    def __init__(self, payload: Dict[str, Any]) -> None:
        self._payload = payload
        self.text = "User-agent: *\nAllow: /intraday/"

    def json(self) -> Dict[str, Any]:
        """Return the stored payload as JSON."""
        return self._payload

    def raise_for_status(self) -> None:  # pragma: no cover - simple stub
        """Do nothing to emulate a successful HTTP response."""
        return self._payload

    def raise_for_status(self) -> None:  # pragma: no cover - simple stub
        return None


class DummySession:
    """Very small HTTP session stub that records calls."""

    def __init__(self, response: DummyResponse) -> None:
        """Store the dummy response returned for every request."""
    def __init__(self, response: DummyResponse) -> None:
        self.response = response
        self.calls = []

    def get(self, url: str, **kwargs: Any) -> DummyResponse:  # pragma: no cover - trivial
        """Return the stored response and track the call arguments."""
        self.calls.append((url, kwargs))
        return self.response


@pytest.fixture
def allow_all_parser() -> robotparser.RobotFileParser:
    """Provide a robots parser that allows all paths."""
class RecordingSession(DummySession):
    def __init__(self, robots_response: DummyResponse) -> None:
        super().__init__(robots_response)
        self._robots_called = False

    def get(self, url: str, **kwargs: Any) -> DummyResponse:
        self.calls.append((url, kwargs))
        if not self._robots_called:
            self._robots_called = True
            return self.response
        raise requests.RequestException("Data fetch blocked for test")


@pytest.fixture
def allow_all_parser() -> robotparser.RobotFileParser:
    parser = robotparser.RobotFileParser()
    parser.parse(["User-agent: *", "Allow: /"])
    return parser


def test_scraper_uses_cache(tmp_path: Path, allow_all_parser: robotparser.RobotFileParser) -> None:
    """Repeated calls should hit the cache and avoid multiple HTTP requests."""
    payload = {"prices": [{"timestamp": "2024-01-01T09:30:00Z", "open": 1, "high": 1, "low": 1, "close": 1, "volume": 1}]}
    session = DummySession(DummyResponse(payload))
    config = ScraperConfig(base_url="https://example.com", endpoint="intraday", cache_dir=tmp_path)
    payload = {"prices": [{"timestamp": "2024-01-01T09:30:00Z", "open": 1, "high": 1, "low": 1, "close": 1, "volume": 1}]}
    session = DummySession(DummyResponse(payload))
    config = ScraperConfig(base_url="https://example.com/api", endpoint="intraday", cache_dir=tmp_path)
    scraper = MarketDataScraper(config, session=session, robot_parser=allow_all_parser)

    first = scraper.get_intraday_prices("SPY", "start", "end")
    second = scraper.get_intraday_prices("SPY", "start", "end")

    assert first == payload
    assert second == payload
    assert len(session.calls) == 1  # cache hit on second call


def test_scraper_respects_robots(tmp_path: Path) -> None:
    """Scraper should raise when robots.txt forbids the endpoint."""
    assert session.calls[0][0] == "https://example.com/api/intraday"


def test_scraper_preserves_base_path_segments(tmp_path: Path, allow_all_parser: robotparser.RobotFileParser) -> None:
    payload = {"prices": []}
    session = DummySession(DummyResponse(payload))
    config = ScraperConfig(
        base_url="https://example.com/api/",
        endpoint="intraday/",
        cache_dir=tmp_path,
    )
    scraper = MarketDataScraper(config, session=session, robot_parser=allow_all_parser)

    scraper.get_intraday_prices("SPY", "start", "end")

    assert session.calls[0][0] == "https://example.com/api/intraday/"


def test_scraper_respects_robots(tmp_path: Path) -> None:
    parser = robotparser.RobotFileParser()
    parser.parse(["User-agent: *", "Disallow: /intraday/"])
    config = ScraperConfig(base_url="https://example.com", endpoint="intraday", cache_dir=tmp_path)
    scraper = MarketDataScraper(config, session=DummySession(DummyResponse({})), robot_parser=parser)

    with pytest.raises(PermissionError):
        scraper.get_intraday_prices("SPY", "start", "end")


def test_scraper_downloads_root_robots(tmp_path: Path) -> None:
    payload = {"prices": []}
    response = DummyResponse(payload)
    session = RecordingSession(response)
    config = ScraperConfig(base_url="https://example.com/api/v1", endpoint="intraday", cache_dir=tmp_path)
    scraper = MarketDataScraper(config, session=session)

    with pytest.raises(RuntimeError):
        scraper.get_intraday_prices("SPY", "start", "end")

    robots_request = session.calls[0]
    assert robots_request[0] == "https://example.com/robots.txt"
