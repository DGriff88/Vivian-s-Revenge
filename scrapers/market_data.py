"""Market data scraping utilities with caching, robots compliance, and retry logic."""

from __future__ import annotations

import json
import logging
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import urljoin
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
        cache_key = self._make_cache_key(symbol, start, end)
        cache_key = f"{symbol}_{start}_{end}.json"
        cached = self._read_cache(cache_key)
        if cached is not None:
            logger.debug("Cache hit for %s", cache_key)
            return cached

        self._enforce_rate_limit()
        self._ensure_robot_parser()
        endpoint_path = f"/{self.config.endpoint.strip('/')}/"
        if not self._is_allowed(endpoint_path):
            raise PermissionError(f"Robots.txt disallows access to {endpoint_path}")

        response_json = self._request_with_retries(endpoint_path, params)
        endpoint_path = self.config.endpoint.lstrip("/")
        base_url = self._normalize_base_url(self.config.base_url)
        full_url = urljoin(base_url, endpoint_path)
        robots_path = self._format_robots_path(endpoint_path)
        if not self._is_allowed(robots_path):
            raise PermissionError(f"Robots.txt disallows access to {endpoint_path}")

        response_json = self._request_with_retries(full_url, params)
        self._write_cache(cache_key, response_json)
        return response_json

    # Internal helpers -------------------------------------------------

    def _request_with_retries(self, path: str, params: Dict[str, Any]) -> Dict[str, Any]:
        retries = 0
        url = urljoin(self.config.base_url, path)
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

    def _ensure_robot_parser(self) -> None:
        if self._robot_parser is not None:
            return
        robots_url = urljoin(self.config.base_url, "/robots.txt")
        base_url = self._normalize_base_url(self.config.base_url)
        root = self._extract_origin(base_url)
        robots_url = urljoin(root, "robots.txt")
        headers = {"User-Agent": self.config.user_agent}
        try:
            response = self.session.get(robots_url, headers=headers, timeout=self.config.timeout_seconds)
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RuntimeError("Unable to load robots.txt for scraping") from exc
        parser = robotparser.RobotFileParser()
        parser.parse(response.text.splitlines())
        self._robot_parser = parser

    def _is_allowed(self, path: str) -> bool:
        assert self._robot_parser is not None, "Robot parser must be initialized"
        return self._robot_parser.can_fetch(self.config.user_agent, path)
    def _is_allowed(self, url_or_path: str) -> bool:
        assert self._robot_parser is not None, "Robot parser must be initialized"
        path = urlsplit(url_or_path).path
        if not path:
            path = url_or_path
        primary_allowed = self._robot_parser.can_fetch(self.config.user_agent, path)
        if path.endswith("/"):
            return primary_allowed
        alt_path = f"{path.rstrip('/')}/"
        return primary_allowed and self._robot_parser.can_fetch(self.config.user_agent, alt_path)

    @staticmethod
    def _normalize_base_url(base_url: str) -> str:
        if base_url.endswith("/"):
            return base_url
        return f"{base_url}/"

    @staticmethod
    def _format_robots_path(endpoint_path: str) -> str:
        normalized = endpoint_path.lstrip("/")
        if not normalized:
            return "/"
        robots_path = f"/{normalized}"
        if robots_path.endswith("/"):
            return robots_path
        return f"{robots_path}/"

    @staticmethod
    def _extract_origin(url: str) -> str:
        parts = urlsplit(url)
        return f"{parts.scheme}://{parts.netloc}/"

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

    def _make_cache_key(self, *parts: str) -> str:
        sanitized_parts = (self._sanitize_for_filename(part) for part in parts)
        return "_".join(sanitized_parts) + ".json"

    @staticmethod
    def _sanitize_for_filename(value: str) -> str:
        """Remove characters that are not permitted in Windows filenames."""
        # Replace characters disallowed on Windows (<>:"/\|?*) and control chars.
        sanitized = re.sub(r'[<>:"/\\|?*]', "_", value)
        sanitized = re.sub(r"[\x00-\x1f]", "_", sanitized)
        # Collapse any sequences of whitespace for readability.
        return re.sub(r"\s+", "_", sanitized)

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
