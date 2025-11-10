"""
Base scraper with common functionality for web scraping.

Provides:
- Async HTTP requests with aiohttp
- Rate limiting
- Request retry with exponential backoff
- User-Agent rotation
- Proxy support (optional)
- Error handling and logging
"""

import asyncio
import logging
import random
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

import aiohttp
from aiohttp import ClientSession, ClientTimeout, TCPConnector
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)


@dataclass
class ScraperConfig:
    """Configuration for scraper behavior."""

    # Rate limiting
    requests_per_second: float = 1.0  # Default: 1 request per second
    min_delay_seconds: float = 1.0
    max_delay_seconds: float = 3.0

    # Retry configuration
    max_retries: int = 3
    retry_delay_seconds: float = 2.0
    retry_backoff_factor: float = 2.0  # Exponential backoff multiplier

    # Request timeout
    timeout_seconds: int = 30

    # Connection pool
    max_connections: int = 10
    max_connections_per_host: int = 5

    # User-Agent rotation
    user_agents: List[str] = field(default_factory=lambda: [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
    ])

    # Proxy configuration (optional)
    proxy_url: Optional[str] = None

    # Respect robots.txt
    respect_robots_txt: bool = True


class BaseScraper(ABC):
    """
    Base class for all web scrapers.

    Provides common functionality:
    - Session management
    - Rate limiting
    - Request retry logic
    - User-Agent rotation
    - HTML parsing
    """

    def __init__(self, config: Optional[ScraperConfig] = None):
        """
        Initialize the scraper.

        Args:
            config: Scraper configuration. If None, uses default config.
        """
        self.config = config or ScraperConfig()
        self.session: Optional[ClientSession] = None
        self._last_request_time: Optional[datetime] = None
        self._request_count = 0
        self._error_count = 0

        logger.info(f"Initialized {self.__class__.__name__} with config: {self.config}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

    async def start(self):
        """Initialize the HTTP session."""
        if self.session is None:
            timeout = ClientTimeout(total=self.config.timeout_seconds)
            connector = TCPConnector(
                limit=self.config.max_connections,
                limit_per_host=self.config.max_connections_per_host,
            )

            self.session = ClientSession(
                timeout=timeout,
                connector=connector,
            )
            logger.info(f"{self.__class__.__name__} session started")

    async def close(self):
        """Close the HTTP session."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info(
                f"{self.__class__.__name__} session closed. "
                f"Requests: {self._request_count}, Errors: {self._error_count}"
            )

    def _get_random_user_agent(self) -> str:
        """Get a random User-Agent from the configured list."""
        return random.choice(self.config.user_agents)

    async def _apply_rate_limit(self):
        """Apply rate limiting between requests."""
        if self._last_request_time:
            elapsed = (datetime.now() - self._last_request_time).total_seconds()
            required_delay = 1.0 / self.config.requests_per_second

            if elapsed < required_delay:
                sleep_time = required_delay - elapsed
                # Add random jitter
                sleep_time += random.uniform(
                    self.config.min_delay_seconds,
                    self.config.max_delay_seconds
                )
                logger.debug(f"Rate limiting: sleeping for {sleep_time:.2f}s")
                await asyncio.sleep(sleep_time)

        self._last_request_time = datetime.now()

    async def fetch(
        self,
        url: str,
        method: str = "GET",
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        json: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
        """
        Fetch a URL with retry logic and rate limiting.

        Args:
            url: The URL to fetch
            method: HTTP method (GET, POST, etc.)
            headers: Additional headers
            params: URL parameters
            data: Form data for POST requests
            json: JSON data for POST requests

        Returns:
            Response text if successful, None otherwise
        """
        if not self.session:
            await self.start()

        # Apply rate limiting
        await self._apply_rate_limit()

        # Prepare headers
        request_headers = {
            "User-Agent": self._get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        if headers:
            request_headers.update(headers)

        # Retry logic
        for attempt in range(self.config.max_retries):
            try:
                logger.debug(
                    f"Fetching {url} (attempt {attempt + 1}/{self.config.max_retries})"
                )

                async with self.session.request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    params=params,
                    data=data,
                    json=json,
                    proxy=self.config.proxy_url,
                ) as response:
                    response.raise_for_status()
                    self._request_count += 1

                    text = await response.text()
                    logger.info(
                        f"Successfully fetched {url} "
                        f"(status: {response.status}, length: {len(text)})"
                    )
                    return text

            except aiohttp.ClientError as e:
                self._error_count += 1
                logger.warning(
                    f"Request failed (attempt {attempt + 1}/{self.config.max_retries}): {e}"
                )

                if attempt < self.config.max_retries - 1:
                    # Exponential backoff
                    delay = self.config.retry_delay_seconds * (
                        self.config.retry_backoff_factor ** attempt
                    )
                    logger.info(f"Retrying in {delay:.2f}s...")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"Max retries reached for {url}")
                    return None

            except Exception as e:
                self._error_count += 1
                logger.error(f"Unexpected error fetching {url}: {e}", exc_info=True)
                return None

        return None

    def parse_html(self, html: str, parser: str = "lxml") -> Optional[BeautifulSoup]:
        """
        Parse HTML content into BeautifulSoup object.

        Args:
            html: HTML string
            parser: Parser to use (lxml, html.parser, etc.)

        Returns:
            BeautifulSoup object if successful, None otherwise
        """
        try:
            soup = BeautifulSoup(html, parser)
            return soup
        except Exception as e:
            logger.error(f"Error parsing HTML: {e}", exc_info=True)
            return None

    def get_stats(self) -> Dict[str, int]:
        """Get scraper statistics."""
        return {
            "requests": self._request_count,
            "errors": self._error_count,
            "success_rate": (
                (self._request_count - self._error_count) / self._request_count * 100
                if self._request_count > 0
                else 0.0
            ),
        }

    @abstractmethod
    async def scrape(self) -> List[Dict[str, Any]]:
        """
        Main scraping logic. Must be implemented by subclasses.

        Returns:
            List of scraped data dictionaries
        """
        pass
