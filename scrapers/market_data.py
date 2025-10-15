"""Market data scraping utilities with caching, robots compliance, and retry logic."""

from __future__ import annotations

import json
import logging
import os
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urljoin, urlsplit
from urllib import robotparser

import requests

logger = logging.getLogger(__name__)


@dataclass
class ScraperConfig:
    base_url: str
    endpoint: str
    cache_dir: Path
    cache_ttl_seconds: int = 300
    rate_limit_seconds: float = 1.0
    max_retries: int = 3
    backoff_factor: float = 0.5
    user_agent: str = "VivianRevengeBot/1.0"
    timeout_seconds: int = 10


class MarketDataScraper:
    """Scrape market data while respecting robots.txt, cache, and rate limits."""

    def __init__(
        self,
        config: ScraperConfig,
        session: Optional[requests.Session] = None,
        robot_parser: Optional[robotparser.RobotFileParser] = None,
    ) -> None:
        self.config = config
        self.session = session or requests.Session()
        self._robot_parser = robot_parser
        self._last_request_ts: float = 0.0
        self._cache_dir = config.cache_dir
        self._cache_dir.mkdir(parents=True, exist_ok=True)

    def get_intraday_prices(self, symbol: str, start: str, end: str) -> Dict[str, Any]:
        """Fetch intraday price data for a symbol between two ISO timestamps."""
        params = {
            "symbol": symbol,
            "start": start,
            "end": end,
            "api_key": os.getenv("DATA_API_KEY"),
        }
        cache_key = f"{symbol}_{start}_{end}.json"
        cached = self._read_cache(cache_key)
        if cached is not None:
            logger.debug("Cache hit for %s", cache_key)
            return cached

        self._enforce_rate_limit()
        self._ensure_robot_parser()
        full_url = self._build_endpoint_url()
        if not self._is_allowed(full_url):
            raise PermissionError(
                f"Robots.txt disallows access to {urlsplit(full_url).path or full_url}"
            )

        response_json = self._request_with_retries(full_url, params)
        self._write_cache(cache_key, response_json)
        return response_json

    # Internal helpers -------------------------------------------------

    def _request_with_retries(self, url: str, params: Dict[str, Any]) -> Dict[str, Any]:
        retries = 0
        headers = {"User-Agent": self.config.user_agent}
        while True:
            try:
                response = self.session.get(
                    url,
                    params=params,
                    headers=headers,
                    timeout=self.config.timeout_seconds,
                )
                response.raise_for_status()
                return response.json()
            except requests.RequestException as exc:
                retries += 1
                if retries > self.config.max_retries:
                    logger.error("Scraper failed after %s retries", self.config.max_retries)
                    raise RuntimeError("Failed to retrieve market data") from exc
                sleep_for = self.config.backoff_factor * (2 ** (retries - 1))
                logger.warning("Request failed (%s). Retrying in %.2fs", exc, sleep_for)
                time.sleep(sleep_for)

    def _build_endpoint_url(self) -> str:
        base = self.config.base_url.rstrip("/") + "/"
        endpoint = self.config.endpoint.lstrip("/")
        full_url = urljoin(base, endpoint)

        # Preserve trailing slashes so robots.txt directory rules such as
        # "Disallow: /intraday/" continue to match the requested path.
        if self.config.endpoint.endswith("/") and not full_url.endswith("/"):
            full_url += "/"

        return full_url

    def _ensure_robot_parser(self) -> None:
        if self._robot_parser is not None:
            return
        robots_url = urljoin(self.config.base_url, "/robots.txt")
        headers = {"User-Agent": self.config.user_agent}
        try:
            response = self.session.get(robots_url, headers=headers, timeout=self.config.timeout_seconds)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError("Unable to load robots.txt for scraping") from exc
        parser = robotparser.RobotFileParser()
        parser.parse(response.text.splitlines())
        self._robot_parser = parser

    def _is_allowed(self, url_or_path: str) -> bool:
        assert self._robot_parser is not None, "Robot parser must be initialized"
        path = urlsplit(url_or_path).path
        if not path:
            path = url_or_path
        return self._robot_parser.can_fetch(self.config.user_agent, path)

    def _enforce_rate_limit(self) -> None:
        now = time.monotonic()
        elapsed = now - self._last_request_ts
        if elapsed < self.config.rate_limit_seconds:
            sleep_time = self.config.rate_limit_seconds - elapsed
            logger.debug("Rate limiting for %.3fs", sleep_time)
            time.sleep(sleep_time)
        self._last_request_ts = time.monotonic()

    def _cache_path(self, cache_key: str) -> Path:
        return self._cache_dir / cache_key

    def _read_cache(self, cache_key: str) -> Optional[Dict[str, Any]]:
        path = self._cache_path(cache_key)
        if not path.exists():
            return None
        age = time.time() - path.stat().st_mtime
        if age > self.config.cache_ttl_seconds:
            logger.debug("Cache expired for %s", cache_key)
            return None
        with path.open("r", encoding="utf-8") as file:
            return json.load(file)

    def _write_cache(self, cache_key: str, payload: Dict[str, Any]) -> None:
        path = self._cache_path(cache_key)
        with path.open("w", encoding="utf-8") as file:
            json.dump(payload, file)
