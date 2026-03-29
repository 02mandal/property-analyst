"""Base scraper classes and utilities."""

import logging
import random
import time
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Generator
from dataclasses import dataclass
from typing import Any, Callable

import requests

from config import Config, RateLimitConfig, RetryConfig
from models.property import PropertyRecord

logger = logging.getLogger(__name__)


@dataclass
class ScrapeResult:
    """Result of a scrape operation."""
    record: PropertyRecord | None
    error: str | None = None
    skipped: bool = False
    skipped_reason: str | None = None


class RateLimiter:
    """Token bucket rate limiter per domain."""

    def __init__(self, config: RateLimitConfig | None = None):
        self.config = config or RateLimitConfig()
        self._last_request: dict[str, float] = defaultdict(float)

    def wait(self, domain: str) -> None:
        """Wait if necessary before making a request to domain."""
        last = self._last_request[domain]
        elapsed = time.time() - last

        if elapsed < self.config.min_delay:
            wait_time = self.config.min_delay - elapsed
            wait_time += random.uniform(0, self.config.jitter)
            time.sleep(wait_time)

        self._last_request[domain] = time.time()

    def record_request(self, domain: str) -> None:
        """Record that a request was made to domain."""
        self._last_request[domain] = time.time()


class RetryHandler:
    """Handles retries with exponential backoff."""

    def __init__(self, config: RetryConfig | None = None):
        self.config = config or RetryConfig()

    def backoff_delay(self, attempt: int) -> float:
        """Calculate delay for given retry attempt."""
        delay = self.config.base_delay * (self.config.exponential_base ** attempt)
        delay = min(delay, self.config.max_delay)
        delay += random.uniform(0, self.config.jitter)
        return delay

    def is_retryable(self, status_code: int) -> bool:
        """Check if HTTP status code should trigger a retry."""
        return status_code in (429, 500, 502, 503, 504)


class AbstractScraper(ABC):
    """Abstract base class for property scrapers."""

    name: str

    def __init__(
        self,
        config: Config | None = None,
        rate_limiter: RateLimiter | None = None,
        retry_handler: RetryHandler | None = None,
    ):
        self.config = config or Config()
        self.rate_limiter = rate_limiter or RateLimiter(self.config.rate_limit)
        self.retry_handler = retry_handler or RetryHandler(self.config.retry)
        self._session: requests.Session | None = None

    @property
    def session(self) -> requests.Session:
        if self._session is None:
            self._session = requests.Session()
            self._session.headers.update({"User-Agent": self.config.user_agent})
        return self._session

    def close(self) -> None:
        if self._session:
            self._session.close()
            self._session = None

    def __enter__(self) -> "AbstractScraper":
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    @abstractmethod
    def parse_listing(self, url: str, html: str) -> PropertyRecord:
        """Parse a listing page HTML into a PropertyRecord."""
        pass

    @abstractmethod
    def search_urls(self, criteria: Any) -> list[str]:
        """Generate search URLs from criteria."""
        pass

    @abstractmethod
    def listings_from_search(self, html: str) -> list[str]:
        """Extract listing URLs from a search results page."""
        pass

    def scrape(self, url: str) -> ScrapeResult:
        """Scrape a single listing URL."""
        domain = url.split("/")[2]

        for attempt in range(self.config.retry.max_retries + 1):
            try:
                self.rate_limiter.wait(domain)

                response = self.session.get(url, timeout=30)

                if response.status_code == 404:
                    return ScrapeResult(
                        record=None,
                        error="Listing not found (404)",
                    )

                if self.retry_handler.is_retryable(response.status_code):
                    if attempt < self.config.retry.max_retries:
                        delay = self.retry_handler.backoff_delay(attempt)
                        logger.warning(
                            f"Rate limited (HTTP {response.status_code}), "
                            f"retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                        continue
                    return ScrapeResult(
                        record=None,
                        error=f"Rate limited (HTTP {response.status_code})",
                    )

                response.raise_for_status()

                record = self.parse_listing(url, response.text)
                return ScrapeResult(record=record)

            except requests.exceptions.RequestException as e:
                if attempt < self.config.retry.max_retries:
                    delay = self.retry_handler.backoff_delay(attempt)
                    logger.warning(f"Request failed: {e}, retrying in {delay:.1f}s...")
                    time.sleep(delay)
                    continue
                return ScrapeResult(record=None, error=str(e))

        return ScrapeResult(record=None, error="Max retries exceeded")

    def scrape_many(
        self,
        urls: list[str],
        progress: Callable[[int, int], None] | None = None,
    ) -> Generator[ScrapeResult, None, None]:
        """Scrape multiple listing URLs with rate limiting."""
        total = len(urls)

        for i, url in enumerate(urls, 1):
            if progress:
                progress(i, total)

            yield self.scrape(url)

    def stream(
        self,
        criteria: Any,
        progress: Callable[[int, int], None] | None = None,
    ) -> Generator[ScrapeResult, None, None]:
        """Scrape listings from search criteria."""
        search_urls = self.search_urls(criteria)
        listing_urls: list[str] = []

        for search_url in search_urls:
            domain = search_url.split("/")[2]
            self.rate_limiter.wait(domain)

            try:
                response = self.session.get(search_url, timeout=30)
                response.raise_for_status()
                listing_urls.extend(self.listings_from_search(response.text))
            except requests.exceptions.RequestException as e:
                logger.error(f"Failed to fetch search URL {search_url}: {e}")
                continue

        unique_urls = list(dict.fromkeys(listing_urls))

        if progress:
            progress(0, len(unique_urls))

        yield from self.scrape_many(unique_urls, progress)

    def stream_from_api(
        self,
        criteria: Any,
        progress: Callable[[int, int], None] | None = None,
    ) -> Generator[ScrapeResult, None, None]:
        """Scrape listings using API-based discovery."""
        listing_urls: list[str] = []

        if hasattr(self, "stream_from_api") and callable(getattr(self, "stream_from_api", None)):
            listing_urls = self.stream_from_api(criteria, progress=progress)
        else:
            listing_urls = self.search_urls(criteria)
            if hasattr(self, "listings_from_api"):
                page = 0
                while True:
                    page_urls = self.listings_from_api(criteria, page)
                    if not page_urls:
                        break
                    listing_urls.extend(page_urls)
                    page += 1

        unique_urls = list(dict.fromkeys(listing_urls))

        if progress:
            progress(0, len(unique_urls))

        yield from self.scrape_many(unique_urls, progress)

    def __call__(
        self,
        url_or_urls: str | list[str],
    ) -> PropertyRecord | list[PropertyRecord] | None:
        """Convenience method to scrape URLs."""
        if isinstance(url_or_urls, str):
            result = self.scrape(url_or_urls)
            return result.record
        else:
            results = []
            for result in self.scrape_many(url_or_urls):
                if result.record:
                    results.append(result.record)
            return results
